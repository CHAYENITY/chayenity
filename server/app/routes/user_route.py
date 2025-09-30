from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models import User
from app.schemas.user_schema import (
    UserOut, 
    UserUpdate, 
    LocationUpdate, 
    AvailabilityUpdate, 
    NearbyUsersRequest, 
    NearbyUserOut,
    UserProfileOut
)
from app.crud import user_crud
from app.database.session import get_db
from app.security import get_current_user_with_access_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user_with_access_token)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    return await user_crud.update_user(db, current_user.id, user_update)


@router.post("/me/verify", response_model=UserOut)
async def verify_me(
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    return await user_crud.verify_user(db, current_user.id)


@router.put("/location", response_model=UserOut)
async def update_location(
    location_update: LocationUpdate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    """Update user's fixed location (primarily for Helpers)"""
    return await user_crud.update_user_location(db, current_user.id, location_update)


@router.put("/availability", response_model=UserOut)
async def update_availability(
    availability_update: AvailabilityUpdate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    """Toggle user's availability status (primarily for Helpers)"""
    return await user_crud.update_user_availability(db, current_user.id, availability_update)


@router.get("/profile", response_model=UserProfileOut)
async def get_profile(
    current_user: User = Depends(get_current_user_with_access_token),
):
    """Get complete user profile including location and availability status"""
    # Use a fresh database session to get the most current data
    async for db in get_db():
        profile = await user_crud.get_user_profile(db, current_user.id)
        
        # Check if location exists
        has_location = profile.fixed_location is not None
        
        # Manually construct the response to ensure all fields are included
        return UserProfileOut(
            id=profile.id,
            email=profile.email,
            full_name=profile.full_name,
            profile_image_url=profile.profile_image_url,
            contact_info=profile.contact_info,
            address_text=profile.address_text,
            is_verified=profile.is_verified,
            reputation_score=profile.reputation_score,
            total_reviews=profile.total_reviews,
            is_available=profile.is_available,
            created_at=profile.created_at,
            has_location=has_location
        )


@router.get("/nearby", response_model=List[NearbyUserOut])
async def get_nearby_helpers(
    latitude: float = Query(..., description="Search latitude"),
    longitude: float = Query(..., description="Search longitude"),
    radius: float = Query(5.0, description="Search radius in kilometers"),
    only_available: bool = Query(True, description="Only show available helpers"),
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    """Find nearby helpers using geospatial search"""
    search_request = NearbyUsersRequest(
        latitude=latitude,
        longitude=longitude, 
        radius=radius,
        only_available=only_available
    )
    return await user_crud.get_nearby_helpers(db, search_request)
