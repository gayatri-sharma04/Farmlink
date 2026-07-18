from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.dependencies import get_current_user, get_current_farmer
from app.models.user import User
from typing import List

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
async def get_products(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get all available products with pagination."""
    result = await db.execute(
        select(Product)
        .offset(skip)
        .limit(limit)
    )
    products = result.scalars().all()
    
    # Add farmer_name to each product
    product_list = []
    for product in products:
        # Get farmer details
        farmer_result = await db.execute(
            select(User).where(User.id == product.farmer_id)
        )
        farmer = farmer_result.scalar_one_or_none()
        
        # Create product dict with farmer_name
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "category": product.category,
            "farmer_id": product.farmer_id,
            "farmer_name": farmer.full_name if farmer else None,
            "image_url": product.image_url,
            "is_available": product.is_available,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }
        product_list.append(product_dict)
    
    return product_list


@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    """Create new product (farmers only)."""
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity,
        category=product.category,
        farmer_id=current_user.id,
        image_url=product.image_url
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    # Create product dict with farmer_name
    product_dict = {
        "id": new_product.id,
        "name": new_product.name,
        "description": new_product.description,
        "price": new_product.price,
        "quantity": new_product.quantity,
        "category": new_product.category,
        "farmer_id": new_product.farmer_id,
        "farmer_name": current_user.full_name,
        "image_url": new_product.image_url,
        "is_available": new_product.is_available,
        "created_at": new_product.created_at,
        "updated_at": new_product.updated_at
    }
    
    return product_dict


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get product details by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get farmer details
    farmer_result = await db.execute(
        select(User).where(User.id == product.farmer_id)
    )
    farmer = farmer_result.scalar_one_or_none()
    
    # Create product dict with farmer_name
    product_dict = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "farmer_id": product.farmer_id,
        "farmer_name": farmer.full_name if farmer else None,
        "image_url": product.image_url,
        "is_available": product.is_available,
        "created_at": product.created_at,
        "updated_at": product.updated_at
    }
    
    return product_dict


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, product_update: ProductUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    """Update product (farmers only, owner only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if current_user.id != product.farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    # Get farmer details
    farmer_result = await db.execute(
        select(User).where(User.id == product.farmer_id)
    )
    farmer = farmer_result.scalar_one_or_none()
    
    # Create product dict with farmer_name
    product_dict = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "farmer_id": product.farmer_id,
        "farmer_name": farmer.full_name if farmer else None,
        "image_url": product.image_url,
        "is_available": product.is_available,
        "created_at": product.created_at,
        "updated_at": product.updated_at
    }
    
    return product_dict


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_farmer)):
    """Delete product (farmers only, owner only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if current_user.id != product.farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this product"
        )
    
    await db.delete(product)
    await db.commit()
