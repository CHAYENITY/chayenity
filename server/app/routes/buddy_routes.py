"""
API endpoints for buddy system (favorites/buddies).
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.crud.buddy_crud import buddy_crud
from app.crud import user_crud
from app.schemas.buddy_schemas import (
    BuddyCreate,
    BuddyResponse,
    BuddyListResponse,
    BuddyUpdate,
)
from app.security import get_current_user_with_access_token as get_current_user
from app.models import User


router = APIRouter(prefix="/buddies", tags=["Buddies"])


@router.post("/", response_model=BuddyResponse, status_code=status.HTTP_201_CREATED)
async def add_buddy(
    buddy_create: BuddyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a user to current user's buddy list."""
    # Check if buddy user exists
    buddy_user = await user_crud.get_user_by_id(db, buddy_create.buddy_id)
    if not buddy_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if user is trying to add themselves
    if buddy_create.buddy_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a buddy",
        )

    # Check if already in buddy list
    if await buddy_crud.is_buddy(db, current_user.id, buddy_create.buddy_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already in your buddy list",
        )

    # Store buddy user details before CRUD operation
    buddy_full_name = buddy_user.full_name
    buddy_email = buddy_user.email
    buddy_is_available = buddy_user.is_available
    buddy_reputation_score = buddy_user.reputation_score
    buddy_profile_image_url = buddy_user.profile_image_url

    # Add buddy
    buddy_entry = await buddy_crud.add_buddy(db, buddy_create, current_user.id)

    # Return response with buddy user details
    return BuddyResponse(
        id=buddy_entry.id,
        user_id=buddy_entry.user_id,
        buddy_id=buddy_entry.buddy_id,
        created_at=buddy_entry.created_at,
        notes=buddy_entry.notes,
        buddy_full_name=buddy_full_name,
        buddy_email=buddy_email,
        buddy_is_available=buddy_is_available,
        buddy_reputation_score=buddy_reputation_score,
        buddy_profile_image_url=buddy_profile_image_url,
    )


@router.get("/", response_model=BuddyListResponse)
async def get_buddy_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's buddy list."""
    buddies = await buddy_crud.get_buddy_list(db, current_user.id, skip, limit)

    # Convert to response format with user details
    buddy_responses = []
    for buddy_entry in buddies:
        # Get buddy user details
        buddy_user = await user_crud.get_user_by_id(db, buddy_entry.buddy_id)
        if buddy_user:  # Skip if user was deleted
            buddy_responses.append(
                BuddyResponse(
                    id=buddy_entry.id,
                    user_id=buddy_entry.user_id,
                    buddy_id=buddy_entry.buddy_id,
                    created_at=buddy_entry.created_at,
                    notes=buddy_entry.notes,
                    buddy_full_name=buddy_user.full_name,
                    buddy_email=buddy_user.email,
                    buddy_is_available=buddy_user.is_available,
                    buddy_reputation_score=buddy_user.reputation_score,
                    buddy_profile_image_url=buddy_user.profile_image_url,
                )
            )

    return BuddyListResponse(
        buddies=buddy_responses,
        total=len(buddy_responses),
        skip=skip,
        limit=limit,
    )


@router.get("/available", response_model=BuddyListResponse)
async def get_available_buddies(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get buddies who are currently available (is_available=True)."""
    available_buddies = await buddy_crud.get_available_buddies(
        db, current_user.id, skip, limit
    )

    # Convert to response format with user details
    buddy_responses = []
    for buddy_entry in available_buddies:
        # Get buddy user details
        buddy_user = await user_crud.get_user_by_id(db, buddy_entry.buddy_id)
        if buddy_user:  # Skip if user was deleted
            buddy_responses.append(
                BuddyResponse(
                    id=buddy_entry.id,
                    user_id=buddy_entry.user_id,
                    buddy_id=buddy_entry.buddy_id,
                    created_at=buddy_entry.created_at,
                    notes=buddy_entry.notes,
                    buddy_full_name=buddy_user.full_name,
                    buddy_email=buddy_user.email,
                    buddy_is_available=buddy_user.is_available,
                    buddy_reputation_score=buddy_user.reputation_score,
                    buddy_profile_image_url=buddy_user.profile_image_url,
                )
            )

    return BuddyListResponse(
        buddies=buddy_responses,
        total=len(buddy_responses),
        skip=skip,
        limit=limit,
    )


@router.delete("/{buddy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_buddy(
    buddy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a buddy from current user's buddy list."""
    removed = await buddy_crud.remove_buddy(db, buddy_id, current_user.id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buddy not found in your list",
        )


@router.get("/{buddy_id}", response_model=BuddyResponse)
async def get_buddy_details(
    buddy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific buddy."""
    buddy_entry = await buddy_crud.get_buddy_entry(db, current_user.id, buddy_id)
    if not buddy_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buddy not found in your list",
        )

    # Get buddy user details
    buddy_user = await user_crud.get_user_by_id(db, buddy_entry.buddy_id)
    if not buddy_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buddy user not found",
        )

    return BuddyResponse(
        id=buddy_entry.id,
        user_id=buddy_entry.user_id,
        buddy_id=buddy_entry.buddy_id,
        created_at=buddy_entry.created_at,
        notes=buddy_entry.notes,
        buddy_full_name=buddy_user.full_name,
        buddy_email=buddy_user.email,
        buddy_is_available=buddy_user.is_available,
        buddy_reputation_score=buddy_user.reputation_score,
        buddy_profile_image_url=buddy_user.profile_image_url,
    )


@router.put("/{buddy_id}", response_model=BuddyResponse)
async def update_buddy_notes(
    buddy_id: UUID,
    buddy_update: BuddyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update notes for a buddy."""
    buddy_entry = await buddy_crud.get_buddy_entry(db, current_user.id, buddy_id)
    if not buddy_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buddy not found in your list",
        )

    # Update notes
    buddy_entry.notes = buddy_update.notes
    await db.commit()
    await db.refresh(buddy_entry)

    # Get buddy user details for response
    buddy_user = await user_crud.get_user_by_id(db, buddy_entry.buddy_id)
    if not buddy_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buddy user not found",
        )

    return BuddyResponse(
        id=buddy_entry.id,
        user_id=buddy_entry.user_id,
        buddy_id=buddy_entry.buddy_id,
        created_at=buddy_entry.created_at,
        notes=buddy_entry.notes,
        buddy_full_name=buddy_user.full_name,
        buddy_email=buddy_user.email,
        buddy_is_available=buddy_user.is_available,
        buddy_reputation_score=buddy_user.reputation_score,
        buddy_profile_image_url=buddy_user.profile_image_url,
    )