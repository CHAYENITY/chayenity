"""Unified pytest configuration for testing (isolated test DB)

This conftest creates and uses a dedicated test database (POSTGRES_DB_test).
It overrides the app's get_db dependency to yield session bound to the test engine
and provides a test client fixture for API tests.
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
from app.configs.app_config import app_config


# Build a safe test database URL by appending _test to the database name
TEST_DATABASE_URL = str(app_config.SQLALCHEMY_DATABASE_URI).replace(
    app_config.POSTGRES_DB, f"{app_config.POSTGRES_DB}_test"
)

# Test engine and session factory
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestingSessionLocal = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create test database schema once per test session and drop afterwards"""
    async with engine_test.begin() as conn:
        # Ensure PostGIS extension is available for geometry columns
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    # Drop schema after tests to keep environment clean
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh db session for each test using the test engine"""
    async with TestingSessionLocal() as session:
        yield session


async def override_get_db():
    """Dependency override for app get_db to use test session"""
    async with TestingSessionLocal() as session:
        yield session


# Apply dependency override so routes use the test DB
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client(setup_test_database) -> AsyncGenerator:
    """Async HTTP client bound to FastAPI app for integration tests"""
    from httpx import AsyncClient, ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac