from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    instructions: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    instructions: str
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    total_tokens: int = 0

    model_config = {"from_attributes": True}


# ── Document ──────────────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: int
    project_id: int
    filename: str
    file_type: str
    token_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Message / Conversation ────────────────────────────────────────────────────

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: int
    project_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationOut):
    messages: List[MessageOut] = []


# ── Chat request ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None  # None → create new conversation


# Config schemas live in app/routers/config_router.py
