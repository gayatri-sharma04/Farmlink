from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse, OrderListResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new order (all users)."""
    # Convert items to JSON-serializable format (convert UUID to string, Decimal to float)
    items_list = [
        {
            "product_id": str(item.product_id),
            "quantity": item.quantity,
            "price": float(item.price)
        }
        for item in order.items
    ]
    
    new_order = Order(
        user_id=current_user.id,
        items=items_list,
        total_price=order.total_price,
        delivery_address=order.delivery_address,
        notes=order.notes,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order


@router.get("/", response_model=list[OrderListResponse])
async def get_orders(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get current user's orders with pagination."""
    result = await db.execute(
        select(Order).where(Order.user_id == current_user.id).offset(skip).limit(limit)
    )
    orders = result.scalars().all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get order details by ID (user must be order owner)."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if current_user.id != order.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_status(order_id: UUID, status_update: OrderStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update order status (any user can track their order)."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status
    valid_statuses = [s.value for s in OrderStatus]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order.status = status_update.status
    if status_update.notes:
        order.notes = status_update.notes
    
    await db.commit()
    await db.refresh(order)
    return order