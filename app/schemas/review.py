from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    product_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(max_length=1000, default=None)


class ReviewUpdate(BaseModel):
    """Schema for updating an existing review."""
    rating: Optional[int] = Field(ge=1, le=5, default=None)
    comment: Optional[str] = Field(max_length=1000, default=None)


class ReviewResponse(BaseModel):
    """Schema for review response data."""
    id: UUID
    user_id: UUID
    product_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema for returning reviews in list view."""
    id: UUID
    user_id: UUID
    product_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime
