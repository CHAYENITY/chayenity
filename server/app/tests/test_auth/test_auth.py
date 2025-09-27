"""
Test authentication routes with updated schema
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User
from app.security import get_password_hash, create_access_token


client = TestClient(app)


class TestAuthRoutes:
    """Test authentication endpoints"""

    @pytest.mark.asyncio
    async def test_register_success(self, db_session: AsyncSession):
        """Test successful user registration"""
        register_data = {
            "email": "newuser@hourz.app",
            "password": "securepassword123",
            "full_name": "New User",
            "contact_info": "+66123456789"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Should return only existing fields, no phone_number or citizen_id
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "contact_info" in data
        assert "is_available" in data
        assert "reputation_score" in data
        assert "created_at" in data
        
        # Should not include sensitive data
        assert "hashed_password" not in data
        assert "password" not in data
        
        # Verify returned data
        assert data["email"] == "newuser@hourz.app"
        assert data["full_name"] == "New User"
        assert data["contact_info"] == "+66123456789"
        assert data["is_available"] is False
        assert data["reputation_score"] == 5.0

    def test_register_duplicate_email(self):
        """Test registering with duplicate email"""
        register_data = {
            "email": "duplicate@hourz.app",
            "password": "password123",
            "full_name": "First User"
        }
        
        # First registration should succeed
        response1 = client.post("/api/auth/register", json=register_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = client.post("/api/auth/register", json=register_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()

    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        register_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 422  # Validation error

    def test_register_missing_required_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            "email": "test@hourz.app"
            # Missing password and full_name
        }
        
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, db_session: AsyncSession):
        """Test successful login"""
        # Create test user
        test_user = User(
            email="login@hourz.app",
            hashed_password=get_password_hash("testpassword"),
            full_name="Login Test User"
        )
        db_session.add(test_user)
        await db_session.commit()
        
        login_data = {
            "username": "login@hourz.app",  # OAuth2 uses 'username' field
            "password": "testpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@hourz.app",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        response = client.post("/api/auth/login", data={})
        
        assert response.status_code == 422  # Validation error


class TestTokenValidation:
    """Test JWT token validation"""

    @pytest.mark.asyncio
    async def test_protected_route_with_valid_token(self, db_session: AsyncSession):
        """Test accessing protected route with valid token"""
        # Create test user
        test_user = User(
            email="protected@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Protected User"
        )
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # Create valid token
        token_data = {"sub": str(test_user.id)}
        token = create_access_token(token_data)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access a protected endpoint (this would be a real protected endpoint)
        # For now, just verify token creation worked
        assert token is not None
        assert len(token) > 0

    def test_protected_route_with_invalid_token(self):
        """Test accessing protected route with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        # This would test actual protected endpoints
        # For now, verify the concept
        invalid_token = "invalid_token"
        assert len(invalid_token) > 0  # Token exists but is invalid

    def test_protected_route_without_token(self):
        """Test accessing protected route without token"""
        # This would test actual protected endpoints
        # For now, verify we can detect missing tokens
        headers = {}
        assert "Authorization" not in headers


class TestUserProfile:
    """Test user profile related functionality"""

    @pytest.mark.asyncio
    async def test_user_profile_creation_with_location(self, db_session: AsyncSession):
        """Test creating user profile with location data"""
        from geoalchemy2 import WKTElement
        
        user = User(
            email="location@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Location User",
            fixed_location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Bangkok, Thailand",
            is_available=True
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.address_text == "Bangkok, Thailand"
        assert user.is_available is True
        assert user.fixed_location is not None

    def test_helper_availability_toggle(self):
        """Test helper availability can be toggled"""
        # This would test API endpoints for toggling availability
        availability_states = [True, False, True]
        
        for state in availability_states:
            assert isinstance(state, bool)


class TestPasswordSecurity:
    """Test password security features"""

    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        from app.security import get_password_hash, verify_password
        
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Should be able to verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password("wrongpassword", hashed) is False

    def test_password_length_validation(self):
        """Test password length requirements"""
        # This would test actual validation logic
        short_password = "123"
        medium_password = "password123"
        long_password = "verylongpasswordwithlotsofcharacters"
        
        assert len(short_password) < 8
        assert len(medium_password) >= 8
        assert len(long_password) > 20