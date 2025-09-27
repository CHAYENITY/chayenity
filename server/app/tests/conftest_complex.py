"""
Pytest configuration and fixtures for Hourz backend tests
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from sqlmodel import SQLModel

from app.database.session import get_db
from app.main import app
from app.models import User, Gig, GigStatus  # Import specific models
from app.configs.app_config import app_config


# Use simple test database approach
TEST_DATABASE_URL = str(app_config.SQLALCHEMY_DATABASE_URI).replace(
    app_config.POSTGRES_DB, 
    f"{app_config.POSTGRES_DB}_test"
)

# Create test engine
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestingSessionLocal = async_sessionmaker(
    bind=engine_test, 
    class_=AsyncSession, 
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up test database once per session"""
    async with engine_test.begin() as conn:
        # Ensure PostGIS extension is available
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    
    # Cleanup after all tests
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for each test"""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=False)
async def prepare_database(setup_test_database):
    """Prepare database for API tests - only when explicitly requested"""
    yield


# Override the dependency to use test database
async def override_get_db():
    """Override database dependency for testing"""
    async with TestingSessionLocal() as session:
        yield session


# Apply the override
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client(setup_test_database) -> AsyncGenerator:
    """Create test client"""
    from httpx import AsyncClient, ASGITransport
    
    async with AsyncClient(
        transport=ASGITransport(app=app),  # type: ignore
        base_url="http://test"
    ) as ac:
        yield ac