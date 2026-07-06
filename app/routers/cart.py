from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import attributes
from uuid import UUID
from app.database import get_db
from app.models.cart import Cart
from app.models.product import Product
from app.schemas.cart import AddToCartRequest, UpdateCartItemRequest, CartResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/items", response_model=CartResponse)
async def add_to_cart(item: AddToCartRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add product to cart or update quantity if already in cart."""
    # Get or create cart for current user
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        cart = Cart(user_id=current_user.id, items=[], total_price=0)
        db.add(cart)
    
    # Check if product exists
    product_result = await db.execute(select(Product).where(Product.id == item.product_id))
    product = product_result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if product already in cart
    items = cart.items if cart.items else []
    item_found = False
    
    for cart_item in items:
        if cart_item.get("product_id") == str(item.product_id):
            cart_item["quantity"] = item.quantity
            cart_item["price"] = float(item.price)
            item_found = True
            break
    
    if not item_found:
        items.append({
            "product_id": str(item.product_id),
            "quantity": item.quantity,
            "price": float(item.price)
        })
    
    cart.items = items
    attributes.flag_modified(cart, "items")
    
    # Recalculate total price
    total_price = sum(item["quantity"] * item["price"] for item in items)
    cart.total_price = total_price
    
    await db.commit()
    await db.refresh(cart)
    return cart


@router.get("/", response_model=CartResponse)
async def get_cart(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get current user's shopping cart."""
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        cart = Cart(user_id=current_user.id, items=[], total_price=0)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    
    return cart


@router.put("/items/{product_id}", response_model=CartResponse)
async def update_cart_item(product_id: UUID, update: UpdateCartItemRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update quantity of product in cart."""
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    
    items = cart.items if cart.items else []
    item_found = False
    
    for cart_item in items:
        if cart_item.get("product_id") == str(product_id):
            cart_item["quantity"] = update.quantity
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in cart"
        )
    
    cart.items = items
    attributes.flag_modified(cart, "items")
    
    # Recalculate total price
    total_price = sum(item["quantity"] * item["price"] for item in items)
    cart.total_price = total_price
    
    await db.commit()
    await db.refresh(cart)
    return cart


@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_from_cart(product_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Remove product from cart."""
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    
    items = cart.items if cart.items else []
    original_length = len(items)
    items = [item for item in items if item.get("product_id") != str(product_id)]
    
    if len(items) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in cart"
        )
    
    cart.items = items
    attributes.flag_modified(cart, "items")
    
    # Recalculate total price
    total_price = sum(item["quantity"] * item["price"] for item in items)
    cart.total_price = total_price
    
    await db.commit()
    await db.refresh(cart)
    return cart


@router.delete("/", response_model=CartResponse)
async def clear_cart(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Clear entire shopping cart."""
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    
    cart.items = []
    attributes.flag_modified(cart, "items")
    cart.total_price = 0
    
    await db.commit()
    await db.refresh(cart)
    return cart
