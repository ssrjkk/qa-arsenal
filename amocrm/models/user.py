"""User model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User model."""

    id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """User create request."""

    name: str = Field(..., min_length=1)
    email: EmailStr


class UserUpdate(BaseModel):
    """User update request."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserListResponse(BaseModel):
    """User list response."""

    users: list[User]
    total: int
    page: int
    per_page: int
