from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, text as sa_text
from sqlmodel import select
from uuid import UUID
from typing import List
from geoalchemy2 import WKTElement
from app.models import User, Address
from app.schemas.user_schema import UserCreate, UserRegister, UserProfileSetup, UserUpdate, LocationUpdate, AvailabilityUpdate, NearbyUsersRequest, NearbyUserOut


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


async def create_minimal_user(db: AsyncSession, user_data: dict) -> User:
    """
    Step 1: Create user with minimal information (email + password only)
    """
    db_user = User(
        email=user_data["email"].lower(),
        hashed_password=user_data["hashed_password"],
        is_profile_complete=False
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


async def complete_user_profile(db: AsyncSession, user_id: UUID, profile_setup: UserProfileSetup) -> User:
    """
    Step 2: Complete user profile with all required information
    """
    # Get the user
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update profile fields
    user.first_name = profile_setup.first_name
    user.last_name = profile_setup.last_name
    user.bio = profile_setup.bio
    user.phone_number = profile_setup.phone_number
    user.additional_contact = profile_setup.additional_contact
    user.profile_image_url = profile_setup.profile_image_url
    user.is_profile_complete = True
    
    # Create address if provided
    if profile_setup.address:
        from geoalchemy2 import WKTElement
        
        address_data = Address(
            address_text=profile_setup.address.address_text,
            district=profile_setup.address.district,
            province=profile_setup.address.province,
            postal_code=profile_setup.address.postal_code,
            country=profile_setup.address.country,
            user_id=user.id
        )
        
        # Add GPS coordinates if provided
        if profile_setup.address.latitude and profile_setup.address.longitude:
            point = WKTElement(f'POINT({profile_setup.address.longitude} {profile_setup.address.latitude})', srid=4326)
            address_data.location = point
        
        db.add(address_data)
    
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to complete profile") from exc


async def create_user(db: AsyncSession, user: UserCreate, password_hash: str) -> User:
    """
    Legacy method - creates user with complete profile information in one step
    """
    # Normalize email to avoid case-duplicate users
    normalized_email = user.email.lower() if user.email else user.email
    db_user = User(
        email=normalized_email,
        hashed_password=password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        phone_number=user.phone_number,
        additional_contact=user.additional_contact,
        is_profile_complete=True
    )
    
    try:
        # Add user to database
        db.add(db_user)
        await db.flush()
        
        # Create address if provided
        if user.address:
            from geoalchemy2 import WKTElement
            
            address_data = Address(
                address_text=user.address.address_text,
                district=user.address.district,
                province=user.address.province,
                postal_code=user.address.postal_code,
                country=user.address.country,
                user_id=db_user.id
            )
            
            # Add GPS coordinates if provided
            if user.address.latitude and user.address.longitude:
                point = WKTElement(f'POINT({user.address.longitude} {user.address.latitude})', srid=4326)
                address_data.location = point
            
            db.add(address_data)
        
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
