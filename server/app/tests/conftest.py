"""Unified pytest configuration for testing (isolated test DB)

This conftest creates and uses a dedicated test database (POSTGRES_DB_test).
It overrides the app's get_db dependency to yield session bound to the test engine
and provides a test client fixture for API tests.
"""
import asyncio
import pytest
import pytest_asyncio
import sys
if sys.platform.startswith("win"):
    # Use selector event loop on Windows to avoid asyncpg loop issues
    try:
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    except Exception:
        pass
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel

# Import app_config early so we can construct the test DB URL before
# importing the application module which creates the production engine.
from app.configs.app_config import app_config

# Build a safe test database URL by appending _test to the database name
TEST_DATABASE_URL = str(app_config.SQLALCHEMY_DATABASE_URI).replace(
    app_config.POSTGRES_DB, f"{app_config.POSTGRES_DB}_test"
)

# Create the test engine and session factory before importing the app so we
# can patch the application's DB session to use the test engine during tests.
engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestingSessionLocal = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)

# Now import the app and the production get_db so we can override it.
from app.database import session as prod_session
from app.main import app
from app.database.session import get_db


# Patch the application's DB session objects to use the test engine/sessionmaker
# This prevents the app lifespan from connecting to the real DB during tests.
prod_session.engine = engine_test
prod_session.AsyncSessionLocal = TestingSessionLocal


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


@pytest_asyncio.fixture
async def async_client(setup_test_database) -> AsyncGenerator:
    """Async HTTP client bound to FastAPI app (alias for client fixture)"""
    from httpx import AsyncClient, ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def user_token_headers(async_client) -> dict:
    """Create a user and return auth headers with access token"""
    from uuid import uuid4
    
    # Create unique user data
    email = f"test_{uuid4().hex[:8]}@example.com"
    password = "testpass123"
    
    # Register user (Step 1: Basic registration)
    register_data = {
        "email": email,
        "password": password
    }
    
    register_response = await async_client.post("/api/auth/register", json=register_data)
    assert register_response.status_code in (200, 201), f"Registration failed: {register_response.text}"
    
    # Login to get token
    login_data = {
        "username": email,
        "password": password
    }
    
    login_response = await async_client.post("/api/auth/login", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}