from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app import models, schemas
from app.services import rag as rag_service

router = APIRouter()


@router.get("/", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).order_by(models.Project.updated_at.desc()).all()
    result = []
    for p in projects:
        doc_count = len(p.documents)
        total_tokens = sum(d.token_count for d in p.documents)
        out = schemas.ProjectOut.model_validate(p)
        out.document_count = doc_count
        out.total_tokens = total_tokens
        result.append(out)
    return result


@router.post("/", response_model=schemas.ProjectOut, status_code=201)
def create_project(body: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(**body.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    out = schemas.ProjectOut.model_validate(project)
    out.document_count = 0
    out.total_tokens = 0
    return out


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = _get_or_404(project_id, db)
    out = schemas.ProjectOut.model_validate(p)
    out.document_count = len(p.documents)
    out.total_tokens = sum(d.token_count for d in p.documents)
    return out


@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, body: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    p = _get_or_404(project_id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    db.commit()
    db.refresh(p)
    out = schemas.ProjectOut.model_validate(p)
    out.document_count = len(p.documents)
    out.total_tokens = sum(d.token_count for d in p.documents)
    return out


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = _get_or_404(project_id, db)
    rag_service.delete_project(project_id)
    db.delete(p)
    db.commit()


def _get_or_404(project_id: int, db: Session) -> models.Project:
    p = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p
