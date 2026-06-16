import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from app.database import init_db
from app.routers import chat, documents, files, projects
from app.routers import config_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="BriefScope LOCAL GPU",
    description="Intelligent document agent with RAG, tool calling and file generation.",
    version="1.7.3",
    root_path=os.getenv("ROOT_PATH", "/api/briefscope_local_gpu"),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router,      prefix="/projects", tags=["projects"])
app.include_router(documents.router,     tags=["documents"])
app.include_router(chat.router,          tags=["chat"])
app.include_router(config_router.router, prefix="/config",   tags=["config"])
app.include_router(files.router,         prefix="/files",    tags=["files"])


@app.get("/", include_in_schema=False)
async def root_redirect(request: Request):
    """Send the root path to the SPA, honoring any proxy root_path prefix."""
    root = request.scope.get("root_path", "")
    return RedirectResponse(url=f"{root}/ui/")


@app.get("/health", tags=["system"])
def health():
    return {"status": "healthy", "service": "briefscope-local-gpu"}


_FRONTEND_DIST = os.getenv(
    "FRONTEND_DIST",
    str(Path(__file__).resolve().parent.parent / "frontend_dist"),
)


@app.get("/ui", include_in_schema=False)
@app.get("/ui/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str = ""):
    file_path = Path(_FRONTEND_DIST) / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(Path(_FRONTEND_DIST) / "index.html")
