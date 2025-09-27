"""
Test the User model and authentication for Hourz app
"""
import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, GigStatus, TransactionStatus, MessageType
from app.security import get_password_hash, verify_password


class TestUserModel:
    """Test User model functionality"""

    @pytest.mark.asyncio
    async def test_user_creation(self, db_session: AsyncSession):
        """Test creating a new user"""
        user = User(
            email="test@hourz.app",
            hashed_password=get_password_hash("testpass123"),
            full_name="Test User",
            contact_info="+66123456789",
            address_text="Bangkok, Thailand",
            is_available=True
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@hourz.app"
        assert user.full_name == "Test User"
        assert user.is_available is True
        assert user.reputation_score == 5.0
        assert user.total_reviews == 0
        assert user.is_verified is False
        assert isinstance(user.created_at, datetime)

    @pytest.mark.asyncio
    async def test_password_verification(self):
        """Test password hashing and verification"""
        password = "mysecurepassword"
        hashed = get_password_hash(password)
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        
        # Should fail with wrong password
        assert verify_password("wrongpassword", hashed) is False

    @pytest.mark.asyncio
    async def test_user_relationships(self, db_session: AsyncSession):
        """Test user relationships are properly set up"""
        user = User(
            email="helper@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Helper User"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Check that relationship attributes exist
        assert hasattr(user, 'gigs_created')
        assert hasattr(user, 'gigs_accepted')
        assert hasattr(user, 'reviews_written')
        assert hasattr(user, 'reviews_received')
        assert hasattr(user, 'buddies')
        assert hasattr(user, 'buddy_of')


class TestEnums:
    """Test enum definitions"""

    def test_gig_status_enum(self):
        """Test GigStatus enum values"""
        assert GigStatus.PENDING == "pending"
        assert GigStatus.ACCEPTED == "accepted"
        assert GigStatus.IN_PROGRESS == "in_progress"
        assert GigStatus.COMPLETED == "completed"
        assert GigStatus.CANCELLED == "cancelled"

    def test_transaction_status_enum(self):
        """Test TransactionStatus enum values"""
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.COMPLETED == "completed"
        assert TransactionStatus.CANCELLED == "cancelled"
        assert TransactionStatus.FAILED == "failed"

    def test_message_type_enum(self):
        """Test MessageType enum values"""
        assert MessageType.TEXT == "text"
        assert MessageType.IMAGE == "image"
        assert MessageType.SYSTEM == "system"


@pytest.mark.asyncio
async def test_user_unique_email_constraint(db_session: AsyncSession):
    """Test that email uniqueness is enforced"""
    email = "duplicate@hourz.app"
    
    # Create first user
    user1 = User(
        email=email,
        hashed_password=get_password_hash("password1"),
        full_name="User One"
    )
    
    db_session.add(user1)
    await db_session.commit()
    
    # Try to create second user with same email
    user2 = User(
        email=email,
        hashed_password=get_password_hash("password2"),
        full_name="User Two"
    )
    
    db_session.add(user2)
    
    # Should raise an integrity error
    with pytest.raises(Exception):  # IntegrityError or similar
        await db_session.commit()