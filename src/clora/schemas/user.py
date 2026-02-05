"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user."""

    email: EmailStr
    username: str
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    username: str
    full_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""

    user_id: int | None = None
    username: str | None = None
