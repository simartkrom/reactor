"""Conversation and Memory models - 대화 및 메모리 시스템."""

from enum import Enum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from clora.models.base import Base, TimestampMixin


class MessageRole(str, Enum):
    """메시지 역할."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base, TimestampMixin):
    """대화 세션 모델."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    expert_id: Mapped[int] = mapped_column(ForeignKey("experts.id"), index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    expert: Mapped["Expert"] = relationship("Expert", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base, TimestampMixin):
    """개별 메시지 모델."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[MessageRole]
    content: Mapped[str] = mapped_column(Text)

    # For AI responses - store reasoning separately
    reasoning_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Token usage tracking
    input_tokens: Mapped[int | None] = mapped_column(nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(nullable=True)

    # Relationship
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


# Import here to avoid circular import
from clora.models.user import User
from clora.models.expert import Expert


class Memory(Base, TimestampMixin):
    """메모리 저장 - 중요한 대화 내용을 자동으로 저장."""

    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    expert_id: Mapped[int | None] = mapped_column(ForeignKey("experts.id"), nullable=True)

    # Memory content
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "창업", "투자"

    # Source
    source_conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey("conversations.id"), nullable=True
    )

    # Importance
    importance: Mapped[int] = mapped_column(default=5)  # 1-10 scale

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="memories")
