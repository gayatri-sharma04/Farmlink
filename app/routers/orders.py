# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from uuid import UUID
# from app.database import get_db
# from app.models.order import Order, OrderStatus
# from app.models.product import Product
# from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse, OrderListResponse
# from app.utils.dependencies import get_current_user
# from app.models.user import User

# router = APIRouter(prefix="/orders", tags=["orders"])


# @router.post("/", response_model=OrderResponse)
# async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Create new order (all users)."""
#     # Convert items to JSON-serializable format (convert UUID to string, Decimal to float)
#     items_list = [
#         {
#             "product_id": str(item.product_id),
#             "quantity": item.quantity,
#             "price": float(item.price)
#         }
#         for item in order.items
#     ]
    
#     new_order = Order(
#         user_id=current_user.id,
#         items=items_list,
#         total_price=order.total_price,
#         delivery_address=order.delivery_address,
#         notes=order.notes,
#         status=OrderStatus.PENDING
#     )
#     db.add(new_order)
#     await db.commit()
#     await db.refresh(new_order)
#     return new_order


# @router.get("/", response_model=list[OrderListResponse])
# async def get_orders(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Get current user's orders with pagination."""
#     result = await db.execute(
#         select(Order).where(Order.user_id == current_user.id).offset(skip).limit(limit)
#     )
#     orders = result.scalars().all()
#     return orders


# @router.get("/{order_id}", response_model=OrderResponse)
# async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Get order details by ID (user must be order owner)."""
#     result = await db.execute(select(Order).where(Order.id == order_id))
#     order = result.scalar_one_or_none()
    
#     if order is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
    
#     if current_user.id != order.user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to view this order"
#         )
    
#     return order


# @router.put("/{order_id}", response_model=OrderResponse)
# async def update_order_status(order_id: UUID, status_update: OrderStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Update order status (any user can track their order)."""
#     result = await db.execute(select(Order).where(Order.id == order_id))
#     order = result.scalar_one_or_none()
    
#     if order is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
    
#     # Validate status
#     valid_statuses = [s.value for s in OrderStatus]
#     if status_update.status not in valid_statuses:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
#         )
    
#     order.status = status_update.status
#     if status_update.notes:
#         order.notes = status_update.notes
    
#     await db.commit()
#     await db.refresh(order)
#     return order

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse, OrderListResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])

#  HELPER FUNCTION - Convert UTC to Nepal timezone
def convert_to_nepal_time(dt: datetime) -> datetime:
    """Convert UTC datetime to Nepal Standard Time (UTC+5:45)"""
    if dt is None:
        return None
    
    # Nepal timezone: UTC+5:45
    nepal_tz = timezone(timedelta(hours=5, minutes=45))
    
    # Assume dt is UTC if no timezone info
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Nepal timezone
    return dt.astimezone(nepal_tz)


@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new order and update inventory."""
    try:
        # Verify user is consumer
        if current_user.role != "consumer":
            raise HTTPException(status_code=403, detail="Only consumers can place orders")

        # Convert items to JSON-serializable format and update inventory
        items_list = []
        for item in order.items:
            # Get product
            product_result = await db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalar_one_or_none()
            
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            # Check if enough quantity available
            if product.quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough {product.name} in stock. Available: {product.quantity}, Requested: {item.quantity}"
                )
            
            # DECREASE INVENTORY
            product.quantity -= item.quantity
            if product.quantity < 0:
                product.quantity = 0
            
            items_list.append({
                "product_id": str(item.product_id),
                "product_name": product.name if product else None,
                "quantity": item.quantity,
                "price": float(item.price)
            })
        
        # Create order record
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
        
        # Convert times to Nepal timezone before returning
        new_order.created_at = convert_to_nepal_time(new_order.created_at)
        new_order.updated_at = convert_to_nepal_time(new_order.updated_at)
        
        return new_order
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")


@router.get("/", response_model=list[OrderListResponse])
async def get_orders(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get current user's orders with pagination."""
    
    # If user is CONSUMER: get orders they placed
    if current_user.role == "consumer":
        result = await db.execute(
            select(Order).where(Order.user_id == current_user.id)
            .offset(skip).limit(limit)
            .order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()
    
    # If user is FARMER: get orders containing their products
    elif current_user.role == "farmer":
        # Get all farmer's products
        products_result = await db.execute(
            select(Product).where(Product.farmer_id == current_user.id)
        )
        farmer_products = products_result.scalars().all()
        farmer_product_ids = [str(p.id) for p in farmer_products]
        
        # Get all orders
        all_orders_result = await db.execute(
            select(Order).offset(skip).limit(limit).order_by(Order.created_at.desc())
        )
        all_orders = all_orders_result.scalars().all()
        
        # Filter orders that contain farmer's products
        orders = []
        for order in all_orders:
            # Check if any item in order belongs to this farmer
            for item in order.items:
                if item.get('product_id') in farmer_product_ids:
                    orders.append(order)
                    break
    
    else:
        orders = []
    
    # Convert times to Nepal timezone
    for order in orders:
        order.created_at = convert_to_nepal_time(order.created_at)
        order.updated_at = convert_to_nepal_time(order.updated_at)
    
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
    
    # Convert times to Nepal timezone
    order.created_at = convert_to_nepal_time(order.created_at)
    order.updated_at = convert_to_nepal_time(order.updated_at)
    
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
    
    #  Convert times to Nepal timezone
    order.created_at = convert_to_nepal_time(order.created_at)
    order.updated_at = convert_to_nepal_time(order.updated_at)
    
    return order