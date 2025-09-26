from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from uuid import UUID
from app.models import User
from app.schemas.user_schema import UserCreate, UserUpdate


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
        latitude=user.latitude,
        longitude=user.longitude,
    )
    try:
        # Use a transaction for atomicity if there isn't one already. Tests and
        # some frameworks may provide an outer transaction, so avoid starting
        # a nested top-level transaction which raises an InvalidRequestError.
        if not db.in_transaction():
            async with db.begin():
                db.add(db_user)
        else:
            db.add(db_user)
        # refresh after commit (or after the outer transaction completes)
        await db.refresh(db_user)
        return db_user
    except IntegrityError as exc:
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

    # Use transaction for update if needed
    if not db.in_transaction():
        async with db.begin():
            db.add(db_user)
    else:
        db.add(db_user)

    await db.refresh(db_user)
    return db_user


async def verify_user(db: AsyncSession, user_id: UUID) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_verified = True
    # Use transaction for update if needed
    if not db.in_transaction():
        async with db.begin():
            db.add(db_user)
    else:
        db.add(db_user)

    await db.refresh(db_user)
    return db_user
