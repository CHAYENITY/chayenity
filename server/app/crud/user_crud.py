from fastapi import HTTPException
from geoalchemy2 import WKTElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select


from app.models import User, Address
from app.schemas.user_schema import (
    UserCreate,
    UserProfileUpsert,
)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.address)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate, password_hash: str) -> User:
    db_user = User(
        email=user.email,
        hashed_password=password_hash,
        is_profile_setup=False,
    )
    try:
        db.add(db_user)
        await db.flush()
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc


async def upsert_user_profile(db: AsyncSession, id: str, user_profile: UserProfileUpsert) -> User:
    db_user = await get_user_by_id(db, id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    is_setup = getattr(db_user, "is_profile_setup", False)

    # * CREATE PROFILE
    if not is_setup:
        for field, value in user_profile.model_dump(exclude_unset=True).items():
            if field != "address":
                setattr(db_user, field, value)
        setattr(db_user, "is_profile_setup", True)

        address_data = getattr(user_profile, "address", None)
        if address_data:
            address = Address(
                address_line=address_data.address_line,
                district=address_data.district,
                province=address_data.province,
                postal_code=address_data.postal_code,
                country=address_data.country,
            )
            if address_data.latitude is not None and address_data.longitude is not None:
                point = WKTElement(
                    f"POINT({address_data.longitude} {address_data.latitude})",
                    srid=4326,
                )
                address.location = point  # type: ignore
            db.add(address)
            await db.flush()
            db_user.address_id = address.id

    # * UPDATE PROFILE
    else:
        for field, value in user_profile.model_dump(exclude_unset=True).items():
            if field != "address":
                setattr(db_user, field, value)

        address_data = getattr(user_profile, "address", None)
        if address_data:
            if db_user.address_id is not None:
                address = await db.get(Address, db_user.address_id)
                if address:
                    for field, value in address_data.model_dump(exclude_unset=True).items():
                        if field not in ("latitude", "longitude"):
                            setattr(address, field, value)
                    if address_data.latitude is not None and address_data.longitude is not None:
                        point = WKTElement(
                            f"POINT({address_data.longitude} {address_data.latitude})",
                            srid=4326,
                        )
                        address.location = point  # type: ignore
            else:
                address = Address(
                    address_line=address_data.address_line,
                    district=address_data.district,
                    province=address_data.province,
                    postal_code=address_data.postal_code,
                    country=address_data.country,
                )
                if address_data.latitude is not None and address_data.longitude is not None:
                    point = WKTElement(
                        f"POINT({address_data.longitude} {address_data.latitude})",
                        srid=4326,
                    )
                    address.location = point  # type: ignore
                db.add(address)
                await db.flush()
                db_user.address_id = address.id
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to upsert user profile") from exc


# async def verify_user(db: AsyncSession, user_id: UUID) -> User:
#     stmt = select(User).where(User.id == user_id)
#     result = await db.execute(stmt)
#     db_user = result.scalar_one_or_none()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     db_user.is_verified = True

#     db.add(db_user)
#     await db.flush()
#     if not db.in_transaction():
#         await db.commit()

#     await db.refresh(db_user)
#     return db_user


# async def update_user_location(
#     db: AsyncSession, user_id: UUID, location_update: LocationUpdate
# ) -> User:
#     """Update user's fixed location (primarily for Helpers)"""
#     try:
#         stmt = select(User).where(User.id == user_id)
#         result = await db.execute(stmt)
#         db_user = result.scalar_one_or_none()
#         if not db_user:
#             raise HTTPException(status_code=404, detail="User not found")

#         # Create PostGIS Point with SRID 4326
#         point_wkt = f"POINT({location_update.longitude} {location_update.latitude})"
#         db_user.fixed_location = WKTElement(point_wkt, srid=4326)
#         db_user.address_text = location_update.address_text

#         # Add to session and commit explicitly
#         db.add(db_user)
#         await db.commit()
#         await db.refresh(db_user)

#         return db_user

#     except Exception:
#         await db.rollback()
#         raise


# async def update_user_availability(
#     db: AsyncSession, user_id: UUID, availability_update: AvailabilityUpdate
# ) -> User:
#     """Toggle user's availability status (primarily for Helpers)"""
#     stmt = select(User).where(User.id == user_id)
#     result = await db.execute(stmt)
#     db_user = result.scalar_one_or_none()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     db_user.is_available = availability_update.is_available

#     db.add(db_user)
#     await db.flush()
#     if not db.in_transaction():
#         await db.commit()

#     await db.refresh(db_user)
#     return db_user


# async def get_nearby_helpers(
#     db: AsyncSession, search_request: NearbyUsersRequest
# ) -> List[NearbyUserOut]:
#     """Find nearby available helpers using geospatial search"""
#     # Create search point with SRID 4326
#     search_point = func.ST_SetSRID(
#         func.ST_MakePoint(search_request.longitude, search_request.latitude), 4326
#     )

#     # Use raw SQL for complex geospatial query
#     distance_query = sa_text(
#         """
#         SELECT
#             id,
#             full_name,
#             profile_image_url,
#             reputation_score,
#             total_reviews,
#             is_available,
#             address_text,
#             ST_Distance(
#                 ST_Transform(fixed_location, 3857),
#                 ST_Transform(ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), 3857)
#             ) as distance_meters
#         FROM "user"
#         WHERE
#             fixed_location IS NOT NULL
#             AND ST_DWithin(
#                 ST_Transform(fixed_location, 3857),
#                 ST_Transform(ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), 3857),
#                 :radius_meters
#             )
#             AND (:only_available = false OR is_available = true)
#         ORDER BY distance_meters
#     """
#     )

#     result = await db.execute(
#         distance_query,
#         {
#             "longitude": search_request.longitude,
#             "latitude": search_request.latitude,
#             "radius_meters": search_request.radius * 1000,  # Convert km to meters
#             "only_available": search_request.only_available,
#         },
#     )

#     nearby_users = result.fetchall()

#     # Convert to response schema
#     return [
#         NearbyUserOut(
#             id=user.id,
#             full_name=user.full_name,
#             profile_image_url=user.profile_image_url,
#             reputation_score=user.reputation_score,
#             total_reviews=user.total_reviews,
#             is_available=user.is_available,
#             distance_km=round(user.distance_meters / 1000, 2),  # Convert meters to km
#             address_text=user.address_text,
#         )
#         for user in nearby_users
#     ]


# async def get_user_profile(db: AsyncSession, user_id: UUID) -> User:
#     """Get complete user profile including all fields"""
#     stmt = select(User).where(User.id == user_id)
#     result = await db.execute(stmt)
#     db_user = result.scalar_one_or_none()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
