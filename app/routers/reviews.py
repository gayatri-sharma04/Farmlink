from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.database import get_db
from app.models.review import Review
from app.models.product import Product
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new product review (one review per user per product)."""
    # Check if product exists
    product_result = await db.execute(select(Product).where(Product.id == review.product_id))
    product = product_result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing_review = await db.execute(
        select(Review).where(
            (Review.user_id == current_user.id) & 
            (Review.product_id == review.product_id)
        )
    )
    if existing_review.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already reviewed this product"
        )
    
    # Create new review
    new_review = Review(
        user_id=current_user.id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review


@router.get("/product/{product_id}", response_model=list[ReviewListResponse])
async def get_product_reviews(product_id: UUID, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get all reviews for a specific product with pagination."""
    # Check if product exists
    product_result = await db.execute(select(Product).where(Product.id == product_id))
    product = product_result.scalar_one_or_none()
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Query reviews
    result = await db.execute(
        select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    )
    reviews = result.scalars().all()
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get review details by ID."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: UUID, update: ReviewUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update review (owner only)."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if current_user.id != review.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )
    
    # Update fields
    if update.rating is not None:
        review.rating = update.rating
    if update.comment is not None:
        review.comment = update.comment
    
    await db.commit()
    await db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete review (owner only)."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if current_user.id != review.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    await db.delete(review)
    await db.commit()
