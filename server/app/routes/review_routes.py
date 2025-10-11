"""
Review API routes for Hourz backend
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.security import get_current_user_with_access_token as get_current_user
from app.models import User, Review, Gig
from app.schemas.review_schema import (
    ReviewCreateSchema,
    ReviewUpdateSchema,
    ReviewResponseSchema,
    UserReviewSummarySchema,
    GigReviewsSchema,
    ReviewStatsSchema
)
from app.crud.review_crud import ReviewCRUD
from app.modules.users import user_crud as UserCRUD
from app.crud.gig_crud import GigCRUD

router = APIRouter(prefix="/reviews", tags=["reviews"])


def review_to_response(
    review: Review,
    reviewer_name: Optional[str] = None,
    reviewee_name: Optional[str] = None,
    gig_title: Optional[str] = None
) -> ReviewResponseSchema:
    """Convert Review model to response schema"""
    return ReviewResponseSchema(
        id=review.id,
        gig_id=review.gig_id,
        reviewer_id=review.reviewer_id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        reviewer_name=reviewer_name,
        reviewee_name=reviewee_name,
        gig_title=gig_title
    )


@router.post("", response_model=ReviewResponseSchema)
async def create_review(
    review_data: ReviewCreateSchema,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review after gig completion"""
    
    review = await ReviewCRUD.create_review(session, review_data, current_user.id)
    
    if not review:
        raise HTTPException(
            status_code=400,
            detail="Cannot create review. Gig must be completed, you must be involved in the gig, "
                   "and you cannot review yourself or create duplicate reviews."
        )
    
    # Get additional data for response
    reviewer = await UserCRUD.get_user_by_id(session, review.reviewer_id)
    reviewee = await UserCRUD.get_user_by_id(session, review.reviewee_id)
    gig = await GigCRUD.get_gig_by_id(session, review.gig_id)
    
    return review_to_response(
        review,
        reviewer_name=reviewer.full_name if reviewer else None,
        reviewee_name=reviewee.full_name if reviewee else None,
        gig_title=gig.title if gig else None
    )


@router.get("/user/{user_id}", response_model=UserReviewSummarySchema)
async def get_user_reviews(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=50, description="Number of reviews to return"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user reviews (paginated) with summary statistics"""
    
    # Get user
    user = await UserCRUD.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get reviews and stats
    reviews, total = await ReviewCRUD.get_user_reviews(session, user_id, skip, limit)
    stats = await ReviewCRUD.get_user_review_stats(session, user_id)
    
    # Convert reviews to response format
    review_responses = []
    for review in reviews:
        # Get reviewer and gig info
        reviewer = await UserCRUD.get_user_by_id(session, review.reviewer_id)
        gig = await GigCRUD.get_gig_by_id(session, review.gig_id)
        
        review_responses.append(review_to_response(
            review,
            reviewer_name=reviewer.full_name if reviewer else None,
            reviewee_name=user.full_name,
            gig_title=gig.title if gig else None
        ))
    
    return UserReviewSummarySchema(
        user_id=user_id,
        user_name=user.full_name,
        total_reviews=stats.total_reviews,
        average_rating=stats.average_rating,
        rating_distribution=stats.rating_counts,
        recent_reviews=review_responses
    )


@router.get("/gig/{gig_id}", response_model=GigReviewsSchema)
async def get_gig_reviews(
    gig_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews for a specific gig"""
    
    # Get gig
    gig = await GigCRUD.get_gig_by_id(session, gig_id)
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")
    
    # Get reviews
    reviews = await ReviewCRUD.get_gig_reviews(session, gig_id)
    
    # Convert to response format
    review_responses = []
    for review in reviews:
        reviewer = await UserCRUD.get_user_by_id(session, review.reviewer_id)
        reviewee = await UserCRUD.get_user_by_id(session, review.reviewee_id)
        
        review_responses.append(review_to_response(
            review,
            reviewer_name=reviewer.full_name if reviewer else None,
            reviewee_name=reviewee.full_name if reviewee else None,
            gig_title=gig.title
        ))
    
    return GigReviewsSchema(
        gig_id=gig_id,
        gig_title=gig.title,
        total_reviews=len(reviews),
        reviews=review_responses
    )


@router.put("/{review_id}", response_model=ReviewResponseSchema)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdateSchema,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review (only by the original reviewer)"""
    
    review = await ReviewCRUD.update_review(session, review_id, review_data, current_user.id)
    
    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found or you are not authorized to update it"
        )
    
    # Get additional data for response
    reviewer = await UserCRUD.get_user_by_id(session, review.reviewer_id)
    reviewee = await UserCRUD.get_user_by_id(session, review.reviewee_id)
    gig = await GigCRUD.get_gig_by_id(session, review.gig_id)
    
    return review_to_response(
        review,
        reviewer_name=reviewer.full_name if reviewer else None,
        reviewee_name=reviewee.full_name if reviewee else None,
        gig_title=gig.title if gig else None
    )


@router.delete("/{review_id}")
async def delete_review(
    review_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review (only by the original reviewer)"""
    
    success = await ReviewCRUD.delete_review(session, review_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Review not found or you are not authorized to delete it"
        )
    
    return {"message": "Review deleted successfully"}


@router.get("/my-reviews", response_model=List[ReviewResponseSchema])
async def get_my_reviews(
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(20, ge=1, le=50, description="Number of reviews to return"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reviews written by the current user"""
    
    reviews, total = await ReviewCRUD.get_user_written_reviews(
        session, current_user.id, skip, limit
    )
    
    # Convert to response format
    review_responses = []
    for review in reviews:
        reviewee = await UserCRUD.get_user_by_id(session, review.reviewee_id)
        gig = await GigCRUD.get_gig_by_id(session, review.gig_id)
        
        review_responses.append(review_to_response(
            review,
            reviewer_name=current_user.full_name,
            reviewee_name=reviewee.full_name if reviewee else None,
            gig_title=gig.title if gig else None
        ))
    
    return review_responses


@router.get("/can-review/{gig_id}/{reviewee_id}")
async def can_review_user(
    gig_id: UUID,
    reviewee_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current user can review another user for a specific gig"""
    
    can_review = await ReviewCRUD.can_user_review_gig(
        session, gig_id, current_user.id, reviewee_id
    )
    
    return {
        "can_review": can_review,
        "gig_id": gig_id,
        "reviewer_id": current_user.id,
        "reviewee_id": reviewee_id
    }