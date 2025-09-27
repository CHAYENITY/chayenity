"""
CRUD operations for buddy system (favorites/buddies).
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
from sqlmodel import select, col

from app.models import BuddyList, User
from app.schemas.buddy_schemas import BuddyCreate


class BuddyCRUD:
    """CRUD operations for buddy/favorites system."""

    async def add_buddy(
        self, db: AsyncSession, buddy_create: BuddyCreate, current_user_id: UUID
    ) -> BuddyList:
        """Add a user to current user's buddy list."""
        buddy_entry = BuddyList(
            user_id=current_user_id,
            buddy_id=buddy_create.buddy_id,
            notes=buddy_create.notes,
        )
        db.add(buddy_entry)
        await db.commit()
        await db.refresh(buddy_entry)
        return buddy_entry

    async def remove_buddy(
        self, db: AsyncSession, buddy_id: UUID, current_user_id: UUID
    ) -> bool:
        """Remove a buddy from current user's buddy list."""
        stmt = select(BuddyList).where(
            and_(
                col(BuddyList.user_id) == current_user_id,
                col(BuddyList.buddy_id) == buddy_id,
            )
        )
        result = await db.execute(stmt)
        buddy_entry = result.scalar_one_or_none()

        if buddy_entry:
            await db.delete(buddy_entry)
            await db.commit()
            return True
        return False

    async def get_buddy_list(
        self, db: AsyncSession, current_user_id: UUID, skip: int = 0, limit: int = 50
    ) -> List[BuddyList]:
        """Get current user's buddy list with user details."""
        stmt = (
            select(BuddyList)
            .where(col(BuddyList.user_id) == current_user_id)
            .offset(skip)
            .limit(limit)
            .order_by(col(BuddyList.created_at).desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_available_buddies(
        self, db: AsyncSession, current_user_id: UUID, skip: int = 0, limit: int = 50
    ) -> List[BuddyList]:
        """Get buddies who are currently available (is_available=True)."""
        stmt = (
            select(BuddyList)
            .join(User, col(User.id) == col(BuddyList.buddy_id))
            .where(
                and_(
                    col(BuddyList.user_id) == current_user_id,
                    col(User.is_available) == True,
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(col(BuddyList.created_at).desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def is_buddy(
        self, db: AsyncSession, user_id: UUID, potential_buddy_id: UUID
    ) -> bool:
        """Check if potential_buddy_id is in user_id's buddy list."""
        stmt = select(BuddyList).where(
            and_(
                col(BuddyList.user_id) == user_id,
                col(BuddyList.buddy_id) == potential_buddy_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_buddy_entry(
        self, db: AsyncSession, user_id: UUID, buddy_id: UUID
    ) -> Optional[BuddyList]:
        """Get specific buddy entry."""
        stmt = select(BuddyList).where(
            and_(
                col(BuddyList.user_id) == user_id,
                col(BuddyList.buddy_id) == buddy_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


# Create a global instance
buddy_crud = BuddyCRUD()