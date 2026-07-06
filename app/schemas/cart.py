from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class CartItem(BaseModel):
    """Schema for a single item in cart."""
    product_id: UUID
    quantity: int = Field(ge=1)
    price: Decimal


class AddToCartRequest(BaseModel):
    """Schema for adding item to cart."""
    product_id: UUID
    quantity: int = Field(ge=1)
    price: Decimal


class UpdateCartItemRequest(BaseModel):
    """Schema for updating cart item quantity."""
    quantity: int = Field(ge=1)


class CartResponse(BaseModel):
    """Schema for cart response data."""
    id: UUID
    user_id: UUID
    items: List[CartItem]
    total_price: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    """Schema for single cart item response."""
    product_id: UUID
    quantity: int
    price: Decimal
