from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


def _now() -> datetime:
    """UTC-aware timestamp for all models."""
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    instructions = Column(Text, default="")  # system-level instructions for the agent
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    documents = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan", passive_deletes=True,
    )
    conversations = relationship(
        "Conversation", back_populates="project", cascade="all, delete-orphan", passive_deletes=True,
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename = Column(String(300), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, xlsx, txt, md
    content_text = Column(Text, default="")
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    project = relationship("Project", back_populates="documents")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(300), default="New conversation")
    created_at = Column(DateTime, default=_now)
    # NOTE: updated_at is NOT auto-updated by onupdate alone when child messages
    # are inserted. Touch it explicitly in chat.py when saving messages.
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    project = relationship("Project", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        passive_deletes=True, order_by="Message.created_at",
    )
    summary = relationship(
        "ConversationSummary", back_populates="conversation",
        cascade="all, delete-orphan", passive_deletes=True, uselist=False,
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(20), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    is_compacted = Column(Boolean, default=False, index=True)  # True = merged into summary
    created_at = Column(DateTime, default=_now)

    conversation = relationship("Conversation", back_populates="messages")


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    summary = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    conversation = relationship("Conversation", back_populates="summary")
