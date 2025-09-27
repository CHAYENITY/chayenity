"""
Simple unit tests for Hourz models that don't require database
"""
import pytest
from app.models import GigStatus, TransactionStatus, MessageType, User, Gig
from app.security import get_password_hash, verify_password


class TestEnumsBasic:
    """Test enum definitions without database"""

    def test_gig_status_enum_values(self):
        """Test GigStatus enum values"""
        assert GigStatus.PENDING == "pending"
        assert GigStatus.ACCEPTED == "accepted"
        assert GigStatus.IN_PROGRESS == "in_progress"
        assert GigStatus.COMPLETED == "completed"
        assert GigStatus.CANCELLED == "cancelled"

    def test_transaction_status_enum_values(self):
        """Test TransactionStatus enum values"""
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.COMPLETED == "completed"
        assert TransactionStatus.CANCELLED == "cancelled"
        assert TransactionStatus.FAILED == "failed"

    def test_message_type_enum_values(self):
        """Test MessageType enum values"""
        assert MessageType.TEXT == "text"
        assert MessageType.IMAGE == "image"
        assert MessageType.SYSTEM == "system"


class TestPasswordSecurity:
    """Test password security without database"""

    def test_password_hashing_and_verification(self):
        """Test password hashing and verification"""
        password = "mysecurepassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        
        # Should fail with wrong password
        assert verify_password("wrongpassword", hashed) is False
        assert verify_password("", hashed) is False

    def test_password_hash_unique(self):
        """Test that same password generates different hashes (due to salt)"""
        password = "testpassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
        
        # But both should verify the same password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestModelStructure:
    """Test model structure without database operations"""

    def test_user_model_fields(self):
        """Test that User model has expected fields"""
        # Test we can create a User instance (without saving to DB)
        user_data = {
            "email": "test@hourz.app",
            "hashed_password": "dummy_hash",
            "full_name": "Test User"
        }
        
        # This should not raise an error
        user = User(**user_data)
        
        # Check that required fields are set
        assert user.email == "test@hourz.app"
        assert user.full_name == "Test User"
        assert user.is_available is False  # default value
        assert user.reputation_score == 5.0  # default value
        assert user.total_reviews == 0  # default value
        assert user.is_verified is False  # default value

    def test_gig_model_fields(self):
        """Test that Gig model has expected fields"""
        from uuid import uuid4
        
        gig_data = {
            "title": "Test Gig",
            "description": "Test gig description",
            "duration_hours": 2,
            "budget": 500.0,
            "location": "POINT(100.5018 13.7563)",  # Will be converted to geometry in DB
            "address_text": "Bangkok, Thailand",
            "seeker_id": uuid4()
        }
        
        # This should not raise an error
        gig = Gig(**gig_data)
        
        # Check that required fields are set
        assert gig.title == "Test Gig"
        assert gig.duration_hours == 2
        assert gig.budget == 500.0
        assert gig.status == GigStatus.PENDING  # default value
        assert gig.helper_id is None  # default value