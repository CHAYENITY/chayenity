from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.api_schema import UpdateOut
from app.database.session import get_db
from app.security import get_current_user_with_access_token

from app.modules.users.user_schema import (
    UserOut,
    UserUpdate,
)
from app.modules.users import user_crud

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user_with_access_token)):
    return current_user


@router.put("/me", response_model=UpdateOut)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    result = await user_crud.update_user(db, str(current_user.id), user_update)
    return result


# @router.put("/me", response_model=UserOut)
# async def update_me(
#     user_update: UserUpdate,
#     current_user: User = Depends(get_current_user_with_access_token),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await user_crud.update_user(db, UUID(str(current_user.id)), user_update)


# @router.post("/me/verify", response_model=UserOut)
# async def verify_me(
#     current_user: User = Depends(get_current_user_with_access_token),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await user_crud.verify_user(db, UUID(str(current_user.id)))


# @router.put("/location", response_model=UserOut)
# async def update_location(
#     location_update: LocationUpdate,
#     current_user: User = Depends(get_current_user_with_access_token),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Update user's fixed location (primarily for Helpers)"""
#     return await user_crud.update_user_location(db, UUID(str(current_user.id)), location_update)


# @router.put("/availability", response_model=UserOut)
# async def update_availability(
#     availability_update: AvailabilityUpdate,
#     current_user: User = Depends(get_current_user_with_access_token),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Toggle user's availability status (primarily for Helpers)"""
#     return await user_crud.update_user_availability(
#         db, UUID(str(current_user.id)), availability_update
#     )


# @router.get("/profile", response_model=UserOut)
# async def get_profile(
#     current_user: User = Depends(get_current_user_with_access_token),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Get complete user profile including addresses"""
#     # Get fresh user data with addresses
#     profile = await user_crud.get_user_by_id(db, UUID(str(current_user.id)))
#     if not profile:
#         raise HTTPException(status_code=404, detail="User not found")

#     return profile


# @router.get("/nearby", response_model=List[NearbyUserOut])
# async def get_nearby_helpers(
#     latitude: float = Query(..., description="Search latitude"),
#     longitude: float = Query(..., description="Search longitude"),
#     radius: float = Query(5.0, description="Search radius in kilometers"),
#     only_available: bool = Query(True, description="Only show available helpers"),
#     current_user: User = Depends(get_current_user_with_access_token),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Find nearby helpers using geospatial search"""
#     search_request = NearbyUsersRequest(
#         latitude=latitude, longitude=longitude, radius=radius, only_available=only_available
#     )
#     return await user_crud.get_nearby_helpers(db, search_request)
