"""
Simple pytest configuration for testing
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy import text

from app.database.session import get_db, engine
from app.main import app
from app.models import User, Gig, GigStatus, ChatRoom, Transaction  # Import specific models


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up test database tables once per session"""
    # Create all tables in the existing database
    async with engine.begin() as conn:
        # Ensure PostGIS extension is available
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        # Create all tables - this should be safe in test mode
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    # Note: We don't drop tables as this might be a shared dev database


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """Use the actual database session from the app"""
    async for session in get_db():
        yield session


# Keep the existing app as is - don't override dependencies