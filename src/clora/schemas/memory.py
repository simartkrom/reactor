"""Memory schemas."""

from datetime import datetime

from pydantic import BaseModel


class MemoryCreate(BaseModel):
    """Schema for creating a memory."""

    title: str
    content: str
    category: str | None = None
    expert_id: int | None = None
    importance: int = 5


class MemoryResponse(BaseModel):
    """Schema for memory response."""

    id: int
    title: str
    content: str
    category: str | None
    expert_id: int | None
    importance: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemorySearchResult(BaseModel):
    """Schema for memory search result."""

    memory: MemoryResponse
    relevance_score: float
