from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, text as sa_text
from sqlmodel import select
from uuid import UUID
from typing import List
from geoalchemy2 import WKTElement
from app.models import User
from app.schemas.user_schema import UserCreate, UserUpdate, LocationUpdate, AvailabilityUpdate, NearbyUsersRequest, NearbyUserOut


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    if not email:
        return None
    # normalize email and query using sqlmodel.select + where
    stmt = select(User).where(User.email == email.lower())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate, password_hash: str) -> User:
    # Normalize email to avoid case-duplicate users
    normalized_email = user.email.lower() if user.email else user.email
    db_user = User(
        email=normalized_email,
        hashed_password=password_hash,
        full_name=user.full_name,
        contact_info=user.contact_info,
        address_text=user.address_text,
        # latitude=user.latitude,
        # longitude=user.longitude,
    )
    try:
        # Add, flush, and commit the user to the database
        db.add(db_user)
        await db.flush()
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
        # Rollback the transaction on error
        await db.rollback()
        # Likely unique constraint on email
        raise HTTPException(status_code=409, detail="Email already registered") from exc


async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields that are provided (disallow direct hashed_password updates)
    update_data = user_update.model_dump(exclude_unset=True)
    # Prevent accidental overwrite of password hash via this endpoint
    update_data.pop("hashed_password", None)
    update_data.pop("password", None)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    # Add/flush and commit only if there's no outer transaction. This makes
    # the instance persistent so refresh will succeed and avoids nested
    # transaction errors when tests manage transactions externally.
    db.add(db_user)
    await db.flush()
    if not db.in_transaction():
        await db.commit()

    await db.refresh(db_user)
    return db_user


async def verify_user(db: AsyncSession, user_id: UUID) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_verified = True

    db.add(db_user)
    await db.flush()
    if not db.in_transaction():
        await db.commit()

    await db.refresh(db_user)
    return db_user


async def update_user_location(db: AsyncSession, user_id: UUID, location_update: LocationUpdate) -> User:
    """Update user's fixed location (primarily for Helpers)"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create PostGIS Point with SRID 4326
        point_wkt = f"POINT({location_update.longitude} {location_update.latitude})"
        db_user.fixed_location = WKTElement(point_wkt, srid=4326)
        db_user.address_text = location_update.address_text

        # Add to session and commit explicitly
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
        
    except Exception as e:
        await db.rollback()
        raise


async def update_user_availability(db: AsyncSession, user_id: UUID, availability_update: AvailabilityUpdate) -> User:
    """Toggle user's availability status (primarily for Helpers)"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_available = availability_update.is_available

    db.add(db_user)
    await db.flush()
    if not db.in_transaction():
        await db.commit()

    await db.refresh(db_user)
    return db_user


async def get_nearby_helpers(
    db: AsyncSession, 
    search_request: NearbyUsersRequest
) -> List[NearbyUserOut]:
    """Find nearby available helpers using geospatial search"""
    # Create search point with SRID 4326
    search_point = func.ST_SetSRID(
        func.ST_MakePoint(search_request.longitude, search_request.latitude), 
        4326
    )
    
    # Use raw SQL for complex geospatial query
    distance_query = sa_text("""
        SELECT 
            id,
            full_name,
            profile_image_url,
            reputation_score,
            total_reviews,
            is_available,
            address_text,
            ST_Distance(
                ST_Transform(fixed_location, 3857),
                ST_Transform(ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), 3857)
            ) as distance_meters
        FROM "user"
        WHERE 
            fixed_location IS NOT NULL
            AND ST_DWithin(
                ST_Transform(fixed_location, 3857),
                ST_Transform(ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), 3857),
                :radius_meters
            )
            AND (:only_available = false OR is_available = true)
        ORDER BY distance_meters
    """)
    
    result = await db.execute(distance_query, {
        "longitude": search_request.longitude,
        "latitude": search_request.latitude,
        "radius_meters": search_request.radius * 1000,  # Convert km to meters
        "only_available": search_request.only_available
    })
    
    nearby_users = result.fetchall()
    
    # Convert to response schema
    return [
        NearbyUserOut(
            id=user.id,
            full_name=user.full_name,
            profile_image_url=user.profile_image_url,
            reputation_score=user.reputation_score,
            total_reviews=user.total_reviews,
            is_available=user.is_available,
            distance_km=round(user.distance_meters / 1000, 2),  # Convert meters to km
            address_text=user.address_text
        )
        for user in nearby_users
    ]


async def get_user_profile(db: AsyncSession, user_id: UUID) -> User:
    """Get complete user profile including all fields"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
