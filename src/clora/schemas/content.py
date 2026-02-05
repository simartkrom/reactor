"""Content schemas - FAQ, Tags, Suggested Questions."""

from datetime import datetime

from pydantic import BaseModel


class FAQResponse(BaseModel):
    """Schema for FAQ response."""

    id: int
    question: str
    answer: str
    category: str | None
    order: int

    model_config = {"from_attributes": True}


class FAQCreate(BaseModel):
    """Schema for creating FAQ."""

    question: str
    answer: str
    category: str | None = None
    order: int = 0


class TagResponse(BaseModel):
    """Schema for tag response."""

    id: int
    name: str
    display_name: str
    description: str | None
    color: str | None
    order: int

    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    """Schema for creating tag."""

    name: str
    display_name: str
    description: str | None = None
    color: str | None = None
    order: int = 0


class SuggestedQuestionResponse(BaseModel):
    """Schema for suggested question response."""

    id: int
    expert_id: int | None
    expert_name: str | None = None
    tag_id: int | None
    question: str
    context: str | None
    description: str | None
    is_featured: bool

    model_config = {"from_attributes": True}


class SuggestedQuestionCreate(BaseModel):
    """Schema for creating suggested question."""

    expert_id: int | None = None
    tag_id: int | None = None
    question: str
    context: str | None = None
    description: str | None = None
    is_featured: bool = False


class StatsResponse(BaseModel):
    """Schema for stats response."""

    total_users: int
    total_conversations: int
    total_messages: int
    active_experts: int


class ExpertWithTagsResponse(BaseModel):
    """Schema for expert with tags."""

    id: int
    name: str
    title: str
    organization: str | None
    profile_image_url: str | None
    bio: str | None
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}
