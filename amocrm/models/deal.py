"""Deal model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Deal(BaseModel):
    """Deal model."""

    id: int
    name: str
    price: float
    status: str = "pending"
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None


class DealCreate(BaseModel):
    """Deal create request."""

    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    contact_id: Optional[int] = None
    company_id: Optional[int] = None


class DealUpdate(BaseModel):
    """Deal update request."""

    name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None


class DealListResponse(BaseModel):
    """Deal list response."""

    deals: list[Deal]
    total: int
    page: int
    per_page: int
