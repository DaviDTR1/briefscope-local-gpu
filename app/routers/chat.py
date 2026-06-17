"""
Chat router -- SSE streaming endpoint.

Flow:
1. Build system prompt.
2. Load conversation history.
3. Stream LLM response via SSE.
4. __thinking__ chunks  -> SSE thinking events (UI progress indicator).
5. __file_ready__ chunks -> SSE file_ready events (one per generated file).
   Multiple files can arrive in a single response - no break, keep consuming.
6. Persist full assistant response in DB.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import AsyncGenerator, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app import models, schemas
from app.logging_config import logger
from app.services.context_manager import build_document_context
from app.services.history import get_active_messages, maybe_compact
from app.services.llm.router import stream_chat

router = APIRouter()


@router.post("/projects/{project_id}/chat")
async def chat(
    project_id: int,
    body: schemas.ChatRequest,
    db: Session = Depends(get_db),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    logger.info("Chat request -- project=%s conv=%s", project_id, body.conversation_id)

    if body.conversation_id:
        conv = db.query(models.Conversation).filter(
            models.Conversation.id == body.conversation_id,
            models.Conversation.project_id == project_id,
        ).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = models.Conversation(project_id=project_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        logger.debug("New conversation created: id=%s", conv.id)

    db.add(models.Message(conversation_id=conv.id, role="user", content=body.message))
    conv.updated_at = datetime.now(timezone.utc)
    db.commit()

    # Message that actually reaches the agent for this turn: the clean message
    # plus the ephemeral context note (attachment reference), if any.
    agent_message = body.message
    if body.agent_context and body.agent_context.strip():
        agent_message = f"{body.message}\n\n{body.agent_context.strip()}"

    docs = [
        {
            "id": d.id,
            "filename": d.filename,
            "content_text": d.content_text,
            "token_count": d.token_count,
        }
        for d in project.documents
    ]
    try:
        doc_context, used_rag = build_document_context(project_id, docs, agent_message)
    except Exception as exc:
        logger.exception("Error building document context: %s", exc)
        doc_context, used_rag = "", False

    instructions_block = (
        f"PROJECT INSTRUCTIONS:\n{project.instructions}"
        if project.instructions.strip()
        else ""
    )

    history = get_active_messages(conv)
    if history and history[-1]["role"] == "user" and history[-1]["content"] == body.message:
        history = history[:-1]
    history.append({"role": "user", "content": agent_message})

    logger.debug(
        "Streaming -- project=%s conv=%s rag=%s msgs=%s",
        project_id, conv.id, used_rag, len(history),
    )

    doc_names = [d.filename for d in project.documents]

    return StreamingResponse(
        _sse_generator(
            body.message, history, instructions_block, doc_context,
            conv.id, used_rag, project_id, doc_names, bool(body.web_search),
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/projects/{project_id}/conversations", response_model=List[schemas.ConversationOut])
def list_conversations(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    active_count_sq = (
        db.query(
            models.Message.conversation_id,
            func.count(models.Message.id).label("active_count"),
        )
        .filter(models.Message.is_compacted.is_(False))
        .group_by(models.Message.conversation_id)
        .subquery()
    )
    rows = (
        db.query(models.Conversation, active_count_sq.c.active_count)
        .outerjoin(active_count_sq, models.Conversation.id == active_count_sq.c.conversation_id)
        .filter(models.Conversation.project_id == project_id)
        .order_by(models.Conversation.updated_at.desc())
        .all()
    )
    result = []
    for conv, active_count in rows:
        out = schemas.ConversationOut.model_validate(conv)
        out.message_count = active_count or 0
        result.append(out)
    return result


@router.get(
    "/projects/{project_id}/conversations/{conv_id}",
    response_model=schemas.ConversationDetail,
)
def get_conversation(project_id: int, conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(
        models.Conversation.id == conv_id,
        models.Conversation.project_id == project_id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    out = schemas.ConversationDetail.model_validate(conv)
    out.message_count = len([m for m in conv.messages if not m.is_compacted])
    out.messages = [
        schemas.MessageOut.model_validate(m)
        for m in conv.messages
        if not m.is_compacted
    ]
    return out


@router.delete("/projects/{project_id}/conversations/{conv_id}", status_code=204)
def delete_conversation(project_id: int, conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(
        models.Conversation.id == conv_id,
        models.Conversation.project_id == project_id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    logger.info("Conversation %s deleted", conv_id)


async def _sse_generator(
    user_message: str,
    messages: List[dict],
    instructions: str,
    doc_context: str,
    conv_id: int,
    used_rag: bool,
    project_id: int = 0,
    doc_names: list[str] | None = None,
    web_search: bool = False,
) -> AsyncGenerator[bytes, None]:
    full_response = ""
    generated_files: list[str] = []

    yield _sse("meta", json.dumps({"conversation_id": conv_id, "rag_active": used_rag}))

    try:
        async for chunk in stream_chat(
            messages,
            instructions=instructions,
            doc_context=doc_context,
            doc_names=doc_names or [],
            project_id=project_id,
            web_search=web_search,
        ):
            # Thinking status event
            if chunk.startswith('{"__thinking__"'):
                try:
                    payload = json.loads(chunk)
                    yield _sse("thinking", payload.get("__thinking__", ""))
                except Exception:
                    pass
                continue

            # File ready event — emit SSE, continue consuming (multiple files possible)
            if chunk.startswith('{"__file_ready__"'):
                try:
                    payload = json.loads(chunk)
                    filename = payload["filename"]
                    formato  = payload.get("formato", "")
                    yield _sse("file_ready", json.dumps({"filename": filename, "formato": formato}))
                    generated_files.append(filename)
                    logger.info("File generated: %s", filename)
                except Exception as exc:
                    logger.exception("Error processing __file_ready__: %s", exc)
                continue

            full_response += chunk
            yield _sse("token", chunk)

    except Exception as exc:
        logger.exception("Error in stream_chat: %s", exc)
        yield _sse("error", str(exc))
        yield _sse("done", "")
        return

    # Build final response text to persist
    if generated_files:
        files_note = "\n".join(f"[Generated file: {f}]" for f in generated_files)
        full_response = (full_response + "\n" + files_note).strip()

    if full_response:
        db = SessionLocal()
        try:
            conv = db.query(models.Conversation).filter(
                models.Conversation.id == conv_id
            ).first()
            if conv:
                db.add(models.Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=full_response,
                ))
                if conv.title == "New conversation":
                    conv.title = user_message[:60] + ("..." if len(user_message) > 60 else "")
                conv.updated_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(conv)
                await maybe_compact(conv, db)
                logger.debug("Response persisted -- conv=%s chars=%s", conv_id, len(full_response))
        except Exception as exc:
            logger.exception("Error persisting response: %s", exc)
            yield _sse("error", f"Error saving response: {exc}")
        finally:
            db.close()

    yield _sse("done", "")


def _sse(event: str, data: str) -> bytes:
    # Emit one ``data:`` line per newline so that markdown line breaks in
    # streamed tokens survive SSE framing (a raw "\n" inside data would
    # otherwise terminate the event early and drop the newline). The client
    # rejoins multiple data lines with "\n".
    body = "".join(f"data: {line}\n" for line in data.split("\n"))
    return f"event: {event}\n{body}\n".encode()
