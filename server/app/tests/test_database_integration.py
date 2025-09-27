"""
Database integration tests for Hourz app with PostGIS
"""
import pytest
from uuid import uuid4
from geoalchemy2 import WKTElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Gig, GigStatus
from app.security import get_password_hash


class TestDatabaseIntegration:
    """Test database operations with PostGIS"""

    @pytest.mark.asyncio
    async def test_user_creation_with_location(self, db_session: AsyncSession):
        """Test creating a user with PostGIS location"""
        user = User(
            email="location@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Location User",
            fixed_location=WKTElement("POINT(100.5018 13.7563)", srid=4326),  # Bangkok coordinates
            address_text="Bangkok, Thailand",
            is_available=True
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "location@hourz.app"
        assert user.address_text == "Bangkok, Thailand"
        assert user.is_available is True
        assert user.fixed_location is not None

    @pytest.mark.asyncio
    async def test_gig_creation_with_location(self, db_session: AsyncSession):
        """Test creating a gig with PostGIS location"""
        # First create a seeker user
        seeker = User(
            email="seeker@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Seeker User"
        )
        db_session.add(seeker)
        await db_session.commit()
        await db_session.refresh(seeker)
        
        # Create a gig with location
        gig = Gig(
            title="Fix leaky faucet",
            description="Need someone to fix a leaky kitchen faucet",
            duration_hours=2,
            budget=500.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),  # Bangkok coordinates
            address_text="123 Sukhumvit Road, Bangkok",
            seeker_id=seeker.id
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig)
        
        assert gig.id is not None
        assert gig.title == "Fix leaky faucet"
        assert gig.budget == 500.0
        assert gig.status == GigStatus.PENDING
        assert gig.seeker_id == seeker.id
        assert gig.location is not None

    @pytest.mark.asyncio  
    async def test_gig_acceptance_workflow(self, db_session: AsyncSession):
        """Test complete gig workflow from creation to acceptance"""
        # Create seeker
        seeker = User(
            email="seeker2@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Seeker User 2"
        )
        
        # Create helper
        helper = User(
            email="helper2@hourz.app", 
            hashed_password=get_password_hash("password"),
            full_name="Helper User 2",
            is_available=True,
            fixed_location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Bangkok, Thailand"
        )
        
        db_session.add_all([seeker, helper])
        await db_session.commit()
        await db_session.refresh(seeker)
        await db_session.refresh(helper)
        
        # Create gig
        gig = Gig(
            title="Clean apartment",
            description="Need help cleaning a 1-bedroom apartment",
            duration_hours=3,
            budget=800.0,
            location=WKTElement("POINT(100.5118 13.7663)", srid=4326),  # Nearby location
            address_text="456 Silom Road, Bangkok",
            seeker_id=seeker.id
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig)
        
        # Accept the gig
        gig.helper_id = helper.id
        gig.status = GigStatus.ACCEPTED
        
        await db_session.commit()
        await db_session.refresh(gig)
        
        assert gig.helper_id == helper.id
        assert gig.status == GigStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_user_relationships(self, db_session: AsyncSession):
        """Test user relationships work correctly"""
        # Create users
        seeker = User(
            email="relationship_seeker@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Relationship Seeker"
        )
        
        helper = User(
            email="relationship_helper@hourz.app",
            hashed_password=get_password_hash("password"), 
            full_name="Relationship Helper",
            is_available=True
        )
        
        db_session.add_all([seeker, helper])
        await db_session.commit()
        await db_session.refresh(seeker)
        await db_session.refresh(helper)
        
        # Create gig
        gig = Gig(
            title="Test relationships",
            description="Testing gig relationships",
            duration_hours=1,
            budget=200.0,
            location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
            address_text="Test Address",
            seeker_id=seeker.id,
            helper_id=helper.id
        )
        
        db_session.add(gig)
        await db_session.commit()
        await db_session.refresh(gig, ['seeker', 'helper'])
        
        # Test relationships
        assert gig.seeker.id == seeker.id
        assert gig.seeker.full_name == "Relationship Seeker"
        assert gig.helper is not None
        assert gig.helper.id == helper.id
        assert gig.helper.full_name == "Relationship Helper"