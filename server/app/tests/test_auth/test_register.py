import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, contact_info",
    [
        ("test1@example.com", "0812345678"),
        ("test2@example.com", "0823456789"),
        ("test3@example.com", "1234567"),
        ("test4@example.com", "123456789012345"),
    ],
)
async def test_register_success_multiple_cases(prepare_database, email, contact_info):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "contact_info": contact_info,
                "full_name": "ชื่อภาษาไทย นามสกุลภาษาไทย",
                "password": "password",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == email
        assert data.get("contact_info") == contact_info
        assert "id" in data
        assert "created_at" in data
        # Basic sanity checks for fields provided by the current schema
        assert data["is_verified"] in (True, False)
        assert isinstance(data["reputation_score"], float)


@pytest.mark.asyncio
async def test_register_email_taken(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/auth/register",
            json={
                "email": "taken@example.com",
                "contact_info": "0123456789",
                "full_name": "ชื่อภาษาไทย นามสกุลภาษาไทย",
                "password": "password",
            },
        )
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "taken@example.com",
                "contact_info": "1234567890",
                "full_name": "ชื่อภาษาไทย นามสกุลภาษาไทย",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_invalid_email_format(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "contact_info": "0123456789",
                "full_name": "ชื่อภาษาไทย นามสกุลภาษาไทย",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phone",
    ["123 456 789", "+66812345678", "abcdefghijk", "123456", "1234567890123456", 1, ""],
)
async def test_register_invalid_contact_info_format(phone, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "validphone@example.com",
                "contact_info": phone,
                "full_name": "ชื่อภาษาไทย นามสกุลภาษาไทย",
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "full_name",
    ["John", 1, "", " "],
)
async def test_register_invalid_full_name(full_name, prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "valid@example.com",
                "contact_info": "0123456789",
                "full_name": full_name,
                "password": "password",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
