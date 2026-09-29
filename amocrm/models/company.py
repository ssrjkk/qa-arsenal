"""Company model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Company(BaseModel):
    """Company model."""

    id: int
    name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


class CompanyCreate(BaseModel):
    """Company create request."""

    name: str = Field(..., min_length=1)
    website: Optional[str] = None
    phone: Optional[str] = None


class CompanyUpdate(BaseModel):
    """Company update request."""

    name: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None


class CompanyListResponse(BaseModel):
    """Company list response."""

    companies: list[Company]
    total: int
    page: int
    per_page: int
