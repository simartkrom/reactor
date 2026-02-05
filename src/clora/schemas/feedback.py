"""Feedback schemas."""

from datetime import datetime

from pydantic import BaseModel

from clora.models.feedback import FeedbackType


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""

    feedback_type: FeedbackType = FeedbackType.REVIEW
    content: str
    rating: int | None = None
    expert_id: int | None = None
    is_anonymous: bool = False
    display_name: str | None = None


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""

    id: int
    feedback_type: FeedbackType
    content: str
    rating: int | None
    expert_id: int | None
    is_featured: bool
    is_anonymous: bool
    display_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CloneRequestCreate(BaseModel):
    """Schema for creating a clone request."""

    expert_name: str
    expert_title: str | None = None
    reason: str
    reference_urls: list[str] | None = None


class CloneRequestResponse(BaseModel):
    """Schema for clone request response."""

    id: int
    expert_name: str
    expert_title: str | None
    reason: str
    status: str
    vote_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CloneRequestVoteResponse(BaseModel):
    """Schema for vote response."""

    request_id: int
    new_vote_count: int
    voted: bool
