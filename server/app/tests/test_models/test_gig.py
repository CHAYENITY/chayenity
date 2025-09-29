"""
Test the Gig model and gig-related functionality for Hourz app
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import WKTElement

from app.models import User, Gig, GigStatus, ChatRoom, Review
from app.security import get_password_hash


@pytest_asyncio.fixture
async def seeker_user(db_session: AsyncSession):
    """Create a seeker user for testing"""
    user = User(
        email="seeker@hourz.app",
        hashed_password=get_password_hash("password"),
        full_name="Seeker User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def helper_user(db_session: AsyncSession):
    """Create a helper user for testing"""
    user = User(
        email="helper@hourz.app",
        hashed_password=get_password_hash("password"),
        full_name="Helper User",
        is_available=True,
        fixed_location=WKTElement("POINT(100.5018 13.7563)", srid=4326),  # Bangkok coordinates
        address_text="Bangkok, Thailand"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestGigModel:
    """Test Gig model functionality"""

    @pytest.mark.asyncio
    async def test_gig_creation(self, db_session: AsyncSession, seeker_user: User):
        """Test creating a new gig"""
        gig = Gig(
            title="Fix leaky faucet",
            description="Need someone to fix a leaky kitchen faucet. Should take about 2 hours.",
            duration_hours=2,
            budget=500.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="123 Sukhumvit Road, Bangkok",
            seeker_id=seeker_user.id,
            starts_at=datetime.now(timezone.utc) + timedelta(hours=24),
            image_urls=["https://example.com/faucet1.jpg", "https://example.com/faucet2.jpg"]
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig)
        
        assert gig.id is not None
        assert gig.title == "Fix leaky faucet"
        assert gig.duration_hours == 2
        assert gig.budget == 500.0
        assert gig.status == GigStatus.PENDING
        assert gig.seeker_id == seeker_user.id
        assert gig.helper_id is None
        assert isinstance(gig.created_at, datetime)
        assert gig.image_urls is not None
        assert len(gig.image_urls) == 2

    @pytest.mark.asyncio
    async def test_gig_acceptance(self, db_session: AsyncSession, seeker_user: User, helper_user: User):
        """Test gig acceptance workflow"""
        # Create a gig
        gig = Gig(
            title="Clean apartment",
            description="Need help cleaning a 1-bedroom apartment",
            duration_hours=3,
            budget=800.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="456 Silom Road, Bangkok",
            seeker_id=seeker_user.id
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig)
        
        # Accept the gig
        gig.helper_id = helper_user.id
        gig.status = GigStatus.ACCEPTED
        gig.updated_at = datetime.now(timezone.utc)
        
        await db_session.commit()
        await db_session.refresh(gig)
        
        assert gig.helper_id == helper_user.id
        assert gig.status == GigStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_gig_completion_workflow(self, db_session: AsyncSession, seeker_user: User, helper_user: User):
        """Test complete gig workflow from creation to completion"""
        # Create gig
        gig = Gig(
            title="Move furniture",
            description="Need help moving furniture to new apartment",
            duration_hours=4,
            budget=1200.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="789 Phayathai Road, Bangkok",
            seeker_id=seeker_user.id
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig)
        
        # Accept gig
        gig.helper_id = helper_user.id
        gig.status = GigStatus.ACCEPTED
        await db_session.commit()
        
        # Start gig
        gig.status = GigStatus.IN_PROGRESS
        await db_session.commit()
        
        # Complete gig
        gig.status = GigStatus.COMPLETED
        gig.completed_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(gig)
        
        assert gig.status == GigStatus.COMPLETED
        assert gig.completed_at is not None

    @pytest.mark.asyncio
    async def test_gig_relationships(self, db_session: AsyncSession, seeker_user: User, helper_user: User):
        """Test gig relationships with users"""
        gig = Gig(
            title="Test relationships",
            description="Testing gig relationships",
            duration_hours=1,
            budget=200.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Test Address",
            seeker_id=seeker_user.id,
            helper_id=helper_user.id
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig, ['seeker', 'helper'])
        
        # Test relationships are loaded correctly
        assert gig.seeker.id == seeker_user.id
        assert gig.seeker.full_name == "Seeker User"
        assert gig.helper is not None
        assert gig.helper.id == helper_user.id
        assert gig.helper.full_name == "Helper User"

    @pytest.mark.asyncio
    async def test_gig_chat_room_creation(self, db_session: AsyncSession, seeker_user: User, helper_user: User):
        """Test that chat room can be created for a gig"""
        # Create and accept gig
        gig = Gig(
            title="Chat test gig",
            description="Testing chat room creation",
            duration_hours=1,
            budget=300.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Chat Test Address",
            seeker_id=seeker_user.id,
            helper_id=helper_user.id,
            status=GigStatus.ACCEPTED
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig)
        
        # Create chat room for the gig
        chat_room = ChatRoom(gig_id=gig.id)
        db_session.add(chat_room)
        await db_session.commit()
        await db_session.refresh(chat_room, ['gig'])
        
        assert chat_room.gig_id == gig.id
        assert chat_room.gig.title == "Chat test gig"
        assert chat_room.is_active is True


class TestGigFiltering:
    """Test gig filtering and search functionality"""

    @pytest.mark.asyncio
    async def test_gig_status_filtering(self, db_session: AsyncSession, seeker_user: User):
        """Test filtering gigs by status"""
        # Create gigs with different statuses
        pending_gig = Gig(
            title="Pending gig",
            description="This gig is pending",
            duration_hours=1,
            budget=200.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Pending Address",
            seeker_id=seeker_user.id,
            status=GigStatus.PENDING
        )
        
        completed_gig = Gig(
            title="Completed gig",
            description="This gig is completed",
            duration_hours=1,
            budget=200.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Completed Address",
            seeker_id=seeker_user.id,
            status=GigStatus.COMPLETED
        )
        
        db_session.add_all([pending_gig, completed_gig])
        await db_session.commit()
        
        # This would be tested with actual CRUD operations
        # For now, just verify the gigs were created with correct statuses
        await db_session.refresh(pending_gig)
        await db_session.refresh(completed_gig)
        
        assert pending_gig.status == GigStatus.PENDING
        assert completed_gig.status == GigStatus.COMPLETED