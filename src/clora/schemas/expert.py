"""Expert schemas."""

from datetime import datetime

from pydantic import BaseModel, HttpUrl

from clora.models.expert import ExpertCategory, KnowledgeSourceType


class KnowledgeSourceCreate(BaseModel):
    """Schema for creating a knowledge source."""

    source_type: KnowledgeSourceType
    source_url: str | None = None
    source_name: str
    is_auto_update: bool = True


class KnowledgeSourceResponse(BaseModel):
    """Schema for knowledge source response."""

    id: int
    source_type: KnowledgeSourceType
    source_url: str | None
    source_name: str
    is_auto_update: bool
    last_crawled_at: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExpertBase(BaseModel):
    """Base schema for Expert."""

    name: str
    title: str
    organization: str | None = None
    category: ExpertCategory = ExpertCategory.OTHER
    profile_image_url: str | None = None
    bio: str | None = None
    expertise: str | None = None  # JSON list
    speaking_style: str | None = None


class ExpertCreate(ExpertBase):
    """Schema for creating an expert."""

    system_prompt: str | None = None
    knowledge_sources: list[KnowledgeSourceCreate] = []


class ExpertResponse(ExpertBase):
    """Schema for expert response."""

    id: int
    is_active: bool
    is_featured: bool
    knowledge_sources: list[KnowledgeSourceResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpertListResponse(BaseModel):
    """Schema for expert list response."""

    id: int
    name: str
    title: str
    organization: str | None
    category: ExpertCategory
    profile_image_url: str | None
    bio: str | None
    is_featured: bool

    model_config = {"from_attributes": True}
