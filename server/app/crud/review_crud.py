"""
CRUD operations for Review model
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, desc, text as sa_text
from sqlmodel import select, col

from app.models import Review, User, Gig, GigStatus
from app.schemas.review_schema import (
    ReviewCreateSchema,
    ReviewUpdateSchema,
    ReviewStatsSchema
)


class ReviewCRUD:
    """CRUD operations for Review model"""

    @staticmethod
    async def create_review(
        session: AsyncSession,
        review_data: ReviewCreateSchema,
        reviewer_id: UUID
    ) -> Optional[Review]:
        """Create a new review after validation"""
        
        # Verify gig exists and is completed
        gig_query = select(Gig).where(
            and_(
                col(Gig.id) == review_data.gig_id,
                col(Gig.status) == GigStatus.COMPLETED
            )
        )
        gig_result = await session.execute(gig_query)
        gig = gig_result.scalar_one_or_none()
        
        if not gig:
            return None  # Gig not found or not completed
        
        # Verify reviewer is either seeker or helper of this gig
        if reviewer_id not in [gig.seeker_id, gig.helper_id]:
            return None  # Reviewer not involved in this gig
            
        # Verify reviewee is the other party (not the reviewer)
        if review_data.reviewee_id == reviewer_id:
            return None  # Cannot review yourself
            
        if review_data.reviewee_id not in [gig.seeker_id, gig.helper_id]:
            return None  # Reviewee not involved in this gig
        
        # Check if review already exists for this gig + reviewer + reviewee combination
        existing_review_query = select(Review).where(
            and_(
                col(Review.gig_id) == review_data.gig_id,
                col(Review.reviewer_id) == reviewer_id,
                col(Review.reviewee_id) == review_data.reviewee_id
            )
        )
        existing_result = await session.execute(existing_review_query)
        existing_review = existing_result.scalar_one_or_none()
        
        if existing_review:
            return None  # Review already exists
        
        # Create the review
        review = Review(
            gig_id=review_data.gig_id,
            reviewer_id=reviewer_id,
            reviewee_id=review_data.reviewee_id,
            rating=review_data.rating,
            comment=review_data.comment,
            created_at=datetime.now(timezone.utc)
        )
        
        session.add(review)
        await session.commit()
        await session.refresh(review)
        
        # Update reviewee's reputation score
        await ReviewCRUD._update_user_reputation(session, review_data.reviewee_id)
        
        return review

    @staticmethod
    async def get_review_by_id(
        session: AsyncSession,
        review_id: UUID,
        load_relations: bool = True
    ) -> Optional[Review]:
        """Get review by ID with optional relationship loading"""
        query = select(Review).where(col(Review.id) == review_id)
        
        if load_relations:
            query = query.options(
                # Load related objects
                # Note: We'll handle this in the response mapping
            )
        
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_reviews(
        session: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        as_reviewee: bool = True
    ) -> Tuple[List[Review], int]:
        """Get reviews for a user (as reviewee by default, or as reviewer)"""
        
        if as_reviewee:
            filter_condition = col(Review.reviewee_id) == user_id
        else:
            filter_condition = col(Review.reviewer_id) == user_id
            
        # Count total
        count_query = select(func.count()).select_from(Review).where(filter_condition)
        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0
        
        # Get paginated reviews
        query = (
            select(Review)
            .where(filter_condition)
            .order_by(desc(col(Review.created_at)))
            .offset(skip)
            .limit(limit)
        )
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        return list(reviews), total

    @staticmethod
    async def get_gig_reviews(
        session: AsyncSession,
        gig_id: UUID
    ) -> List[Review]:
        """Get all reviews for a specific gig"""
        query = (
            select(Review)
            .where(col(Review.gig_id) == gig_id)
            .order_by(desc(col(Review.created_at)))
        )
        
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_written_reviews(
        session: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Review], int]:
        """Get reviews written by a user"""
        return await ReviewCRUD.get_user_reviews(
            session, user_id, skip, limit, as_reviewee=False
        )

    @staticmethod
    async def update_review(
        session: AsyncSession,
        review_id: UUID,
        review_data: ReviewUpdateSchema,
        reviewer_id: UUID
    ) -> Optional[Review]:
        """Update a review (only by the original reviewer)"""
        
        # Get the review
        review = await ReviewCRUD.get_review_by_id(session, review_id, load_relations=False)
        if not review:
            return None
            
        # Verify the reviewer owns this review
        if review.reviewer_id != reviewer_id:
            return None
            
        # Update fields
        if review_data.rating is not None:
            review.rating = review_data.rating
        if review_data.comment is not None:
            review.comment = review_data.comment
            
        await session.commit()
        await session.refresh(review)
        
        # Update reviewee's reputation score if rating changed
        if review_data.rating is not None:
            await ReviewCRUD._update_user_reputation(session, review.reviewee_id)
        
        return review

    @staticmethod
    async def delete_review(
        session: AsyncSession,
        review_id: UUID,
        reviewer_id: UUID
    ) -> bool:
        """Delete a review (only by the original reviewer)"""
        
        # Get the review
        review = await ReviewCRUD.get_review_by_id(session, review_id, load_relations=False)
        if not review:
            return False
            
        # Verify the reviewer owns this review
        if review.reviewer_id != reviewer_id:
            return False
            
        reviewee_id = review.reviewee_id
        
        await session.delete(review)
        await session.commit()
        
        # Update reviewee's reputation score
        await ReviewCRUD._update_user_reputation(session, reviewee_id)
        
        return True

    @staticmethod
    async def get_user_review_stats(
        session: AsyncSession,
        user_id: UUID
    ) -> ReviewStatsSchema:
        """Get review statistics for a user"""
        
        # Get all ratings for this user as reviewee
        ratings_query = select(col(Review.rating)).where(col(Review.reviewee_id) == user_id)
        ratings_result = await session.execute(ratings_query)
        ratings = [rating for rating in ratings_result.scalars().all()]
        
        if not ratings:
            return ReviewStatsSchema(
                total_reviews=0,
                average_rating=0.0,
                rating_counts={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            )
        
        # Calculate statistics
        total_reviews = len(ratings)
        average_rating = sum(ratings) / total_reviews
        
        # Count each rating
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            rating_counts[rating] += 1
            
        return ReviewStatsSchema(
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2),
            rating_counts=rating_counts
        )

    @staticmethod
    async def _update_user_reputation(session: AsyncSession, user_id: UUID) -> None:
        """Update user's reputation score based on their reviews"""
        
        # Calculate average rating for this user
        avg_query = select(func.avg(col(Review.rating))).where(col(Review.reviewee_id) == user_id)
        avg_result = await session.execute(avg_query)
        avg_rating = avg_result.scalar()
        
        if avg_rating is None:
            avg_rating = 0.0
        
        # Update user's reputation_score
        update_query = sa_text(
            "UPDATE user SET reputation_score = :reputation WHERE id = :user_id"
        )
        await session.execute(
            update_query,
            {"reputation": round(float(avg_rating), 2), "user_id": str(user_id)}
        )
        await session.commit()

    @staticmethod
    async def can_user_review_gig(
        session: AsyncSession,
        gig_id: UUID,
        reviewer_id: UUID,
        reviewee_id: UUID
    ) -> bool:
        """Check if a user can review another user for a specific gig"""
        
        # Get gig details
        gig_query = select(Gig).where(col(Gig.id) == gig_id)
        gig_result = await session.execute(gig_query)
        gig = gig_result.scalar_one_or_none()
        
        if not gig or gig.status != GigStatus.COMPLETED:
            return False
            
        # Check if reviewer is involved in the gig
        if reviewer_id not in [gig.seeker_id, gig.helper_id]:
            return False
            
        # Check if reviewee is the other party
        if reviewee_id not in [gig.seeker_id, gig.helper_id] or reviewee_id == reviewer_id:
            return False
            
        # Check if review already exists
        existing_review_query = select(Review).where(
            and_(
                col(Review.gig_id) == gig_id,
                col(Review.reviewer_id) == reviewer_id,
                col(Review.reviewee_id) == reviewee_id
            )
        )
        existing_result = await session.execute(existing_review_query)
        existing_review = existing_result.scalar_one_or_none()
        
        return existing_review is None