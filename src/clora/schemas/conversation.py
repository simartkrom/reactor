"""Conversation schemas."""

from datetime import datetime

from pydantic import BaseModel

from clora.models.conversation import MessageRole


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    role: MessageRole
    content: str
    reasoning_content: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    expert_id: int
    title: str | None = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: int
    expert_id: int
    title: str | None
    is_active: bool
    messages: list[MessageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    """Schema for chat request."""

    message: str
    conversation_id: int | None = None  # If None, create new conversation
    expert_id: int
    include_memory: bool = True  # 메모리 컨텍스트 포함 여부
    thinking_mode: str = "enabled"  # "enabled" or "disabled"


class ChatResponse(BaseModel):
    """Schema for chat response."""

    conversation_id: int
    message: MessageResponse
    expert_name: str
    memory_saved: bool = False  # 새로운 메모리가 저장되었는지


class ConversationListResponse(BaseModel):
    """Schema for conversation list item."""

    id: int
    expert_id: int
    expert_name: str
    title: str | None
    last_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
