from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class OrderItem(BaseModel):
    """Schema for a single item in an order."""
    product_id: UUID
    product_name: Optional[str] = None
    quantity: int = Field(ge=1)
    price: Decimal


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    items: List[OrderItem] = Field(min_length=1)
    total_price: Decimal
    delivery_address: str = Field(min_length=5)
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: str
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema for order response data."""
    id: UUID
    user_id: UUID
    items: List[OrderItem]
    total_price: Decimal
    status: str
    delivery_address: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for returning order in list view."""
    id: UUID
    user_id: UUID
    items: List[OrderItem]
    total_price: Decimal
    status: str
    delivery_address: Optional[str]
    notes: Optional[str]
    created_at: datetime
