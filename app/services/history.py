"""
Conversation history management with Summary Memory compaction.

After HISTORY_COMPACT_AFTER user turns, older messages are summarized
into ConversationSummary using a lightweight LLM call.
Active history = [summary injection] + recent non-compacted messages.
"""
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session

from app import config, models


def get_active_messages(conversation: models.Conversation) -> List[dict]:
    """
    Build the message list to pass to the LLM:
      [optional summary as system msg] + recent non-compacted messages.
    """
    recent = [
        {"role": m.role, "content": m.content}
        for m in conversation.messages
        if not m.is_compacted
    ]
    if conversation.summary:
        summary_msg = {
            "role": "system",
            "content": (
                "<resumen_conversacion_previa>\n"
                + conversation.summary.summary
                + "\n</resumen_conversacion_previa>"
            ),
        }
        return [summary_msg] + recent
    return recent


async def maybe_compact(conversation: models.Conversation, db: Session) -> None:
    """Compact old messages when user turn count exceeds the configured threshold."""
    threshold = config.get("history_compact_after", 6)
    user_turns = [m for m in conversation.messages if m.role == "user" and not m.is_compacted]
    if len(user_turns) <= threshold:
        return

    active = [m for m in conversation.messages if not m.is_compacted]
    keep   = threshold * 2  # keep last N user+assistant pairs
    to_compact = active[:-keep] if len(active) > keep else []
    if not to_compact:
        return

    history_text = "\n".join(
        f"{m.role.upper()}: {m.content[:500]}" for m in to_compact
    )
    prompt = (
        "Concisely summarize the key points, requested changes and "
        "decisions made in the following conversation:\n\n" + history_text
    )

    summary_text = await _call_fast_llm(prompt)

    if conversation.summary:
        conversation.summary.summary += "\n\n" + summary_text
    else:
        conversation.summary = models.ConversationSummary(
            conversation_id=conversation.id, summary=summary_text
        )
        db.add(conversation.summary)

    for m in to_compact:
        m.is_compacted = True

    db.commit()


async def _call_fast_llm(prompt: str) -> str:
    """Use the active provider (lightweight model) for summarization."""
    mode = config.get("llm_mode", "cloud")
    try:
        if mode == "local":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                base_url=f"{config.get('ollama_host')}/v1",
                api_key="ollama",
            )
            resp = await client.chat.completions.create(
                model=config.get("ollama_model"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""

        provider = config.get("cloud_provider", "anthropic")

        if provider == "anthropic":
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=config.get("anthropic_api_key"))
            msg = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text if msg.content else ""

        if provider == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=config.get("openai_api_key"))
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""

        if provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=config.get("google_api_key"))
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp  = await model.generate_content_async(prompt)
            return resp.text or ""

    except Exception as e:
        return f"[Error compacting history: {e}]"

    return ""
