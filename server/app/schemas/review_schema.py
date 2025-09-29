"""
Review schemas for Hourz backend
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreateSchema(BaseModel):
    """Schema for creating a new review"""
    gig_id: UUID = Field(..., description="ID of the completed gig")
    reviewee_id: UUID = Field(..., description="ID of user being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    comment: str = Field(..., min_length=1, max_length=1000, description="Review comment")


class ReviewUpdateSchema(BaseModel):
    """Schema for updating an existing review"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Updated rating")
    comment: Optional[str] = Field(None, min_length=1, max_length=1000, description="Updated comment")


class ReviewResponseSchema(BaseModel):
    """Schema for review responses"""
    id: UUID
    gig_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    # Related data
    reviewer_name: Optional[str] = None
    reviewee_name: Optional[str] = None
    gig_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserReviewSummarySchema(BaseModel):
    """Schema for user review summary/statistics"""
    user_id: UUID
    user_name: str
    total_reviews: int
    average_rating: float
    rating_distribution: dict[int, int] = Field(description="Count of each star rating (1-5)")
    recent_reviews: List[ReviewResponseSchema] = Field(description="Most recent reviews")

    model_config = ConfigDict(from_attributes=True)


class GigReviewsSchema(BaseModel):
    """Schema for all reviews related to a specific gig"""
    gig_id: UUID
    gig_title: str
    total_reviews: int
    reviews: List[ReviewResponseSchema]
    
    model_config = ConfigDict(from_attributes=True)


class ReviewStatsSchema(BaseModel):
    """Schema for review statistics"""
    total_reviews: int
    average_rating: float
    rating_counts: dict[int, int] = Field(description="Count for each rating 1-5")
    
    model_config = ConfigDict(from_attributes=True)