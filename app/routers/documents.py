from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.services.ingestion import extract_text, infer_file_type, SUPPORTED_EXTENSIONS
from app.services.token_counter import count_tokens
from app.services import rag as rag_service

router = APIRouter()


@router.post("/projects/{project_id}/documents", response_model=schemas.DocumentOut, status_code=201)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Verify project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ext = infer_file_type(file.filename or "")
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    file_bytes = await file.read()
    text = extract_text(file_bytes, file.filename or "document")
    tokens = count_tokens(text)

    doc = models.Document(
        project_id=project_id,
        filename=file.filename or "document",
        file_type=ext,
        content_text=text,
        token_count=tokens,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Index in ChromaDB (async-friendly: runs in thread pool)
    try:
        rag_service.index_document(project_id, doc.id, doc.filename, text)
    except Exception as e:
        # Non-fatal: RAG won't work but in-context still will
        print(f"[briefscope] RAG indexing failed for doc {doc.id}: {e}")

    return schemas.DocumentOut.model_validate(doc)


@router.get("/projects/{project_id}/documents", response_model=List[schemas.DocumentOut])
def list_documents(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    docs = (
        db.query(models.Document)
        .filter(models.Document.project_id == project_id)
        .order_by(models.Document.created_at.asc())
        .all()
    )
    return [schemas.DocumentOut.model_validate(d) for d in docs]


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    rag_service.delete_document(doc.project_id, document_id)
    db.delete(doc)
    db.commit()
