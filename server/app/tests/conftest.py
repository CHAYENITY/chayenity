"""
Pytest configuration and fixtures for Hourz backend tests
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel

from app.database.session import get_db
from app.main import app
from app.models import *  # Import all models to register them
from app.configs.app_config import app_config


# Use PostgreSQL test database with PostGIS
TEST_DATABASE_URL = str(app_config.SQLALCHEMY_DATABASE_URI).replace(
    app_config.POSTGRES_DB, 
    f"{app_config.POSTGRES_DB}_test"
)

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    async with engine_test.begin() as conn:
        # Ensure PostGIS extension is available
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine_test.begin() as conn:
        # Drop all tables after test
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=False)  # Changed to not auto-run
async def prepare_database():
    """Prepare database for API tests - only when explicitly requested"""
    async with engine_test.begin() as conn:
        # Ensure PostGIS extension is available
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=False)  # Changed to not auto-run
async def override_get_db():
    """Override database dependency for API tests - only when explicitly requested"""
    async def _override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()