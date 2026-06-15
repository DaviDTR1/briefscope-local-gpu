from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.documents import (
    list_generated,
    safe_generated_path,
    delete_generated,
)

router = APIRouter()


class FileInfo(BaseModel):
    filename: str
    size: int
    title: str
    created_at: str
    format: str


@router.get("", response_model=list[FileInfo])
@router.get("/", response_model=list[FileInfo], include_in_schema=False)
def list_files(project_id: int = Query(..., description="Owning project id")):
    """List the deliverables generated inside a single project, newest first."""
    return [FileInfo(**e) for e in list_generated(project_id)]


@router.get("/{filename}")
def download_file(
    filename: str,
    project_id: int = Query(..., description="Owning project id"),
):
    path = safe_generated_path(project_id, filename)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    media_types = {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "md": "text/markdown",
        "txt": "text/plain",
    }
    ext = path.suffix.lstrip('.')
    media_type = media_types.get(ext, 'application/octet-stream')
    return FileResponse(path=str(path), filename=filename, media_type=media_type)


@router.delete("/{filename}", status_code=204)
def delete_file(
    filename: str,
    project_id: int = Query(..., description="Owning project id"),
):
    if not delete_generated(project_id, filename):
        raise HTTPException(status_code=404, detail="File not found")
