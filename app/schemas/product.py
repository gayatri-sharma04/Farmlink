from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str = Field(min_length=2)
    description: str = Field(min_length=5)
    price: Decimal
    quantity: int = Field(ge=0)
    category: str = "other"
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema for product response data."""
    id: UUID
    name: str
    description: str
    price: Decimal
    quantity: int
    category: str
    farmer_id: UUID
    image_url: Optional[str]
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
