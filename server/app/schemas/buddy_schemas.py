"""
Pydantic schemas for buddy/favorites system.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class BuddyBase(BaseModel):
    """Base buddy schema."""
    notes: Optional[str] = None


class BuddyCreate(BuddyBase):
    """Schema for creating a buddy entry."""
    buddy_id: UUID


class BuddyUpdate(BuddyBase):
    """Schema for updating a buddy entry."""
    pass


class BuddyResponse(BuddyBase):
    """Schema for buddy response with user details."""
    id: UUID
    user_id: UUID
    buddy_id: UUID
    created_at: datetime
    
    # Nested buddy user info
    buddy_full_name: str
    buddy_email: str
    buddy_is_available: bool
    buddy_reputation_score: float
    buddy_profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class BuddyListResponse(BaseModel):
    """Schema for paginated buddy list."""
    buddies: list[BuddyResponse]
    total: int
    skip: int
    limit: int