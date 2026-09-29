"""Contact model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Contact(BaseModel):
    """Contact model."""

    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None


class ContactCreate(BaseModel):
    """Contact create request."""

    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None


class ContactUpdate(BaseModel):
    """Contact update request."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ContactListResponse(BaseModel):
    """Contact list response."""

    contacts: list[Contact]
    total: int
    page: int
    per_page: int
