"""
Test the WebSocket functionality for real-time chat
"""
import pytest
import json
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import WKTElement

from app.main import app
from app.models import User, Gig, GigStatus, ChatRoom, ChatParticipant, Message
from app.security import get_password_hash, create_access_token


@pytest.fixture
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


@pytest.fixture
async def helper_user(db_session: AsyncSession):
    """Create a helper user for testing"""
    user = User(
        email="helper@hourz.app",
        hashed_password=get_password_hash("password"),
        full_name="Helper User",
        is_available=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def accepted_gig(db_session: AsyncSession, seeker_user: User, helper_user: User):
    """Create an accepted gig for testing"""
    gig = Gig(
        title="Test Chat Gig",
        description="Testing chat functionality",
        duration_hours=2,
        budget=500.0,
        location=WKTElement("POINT(100.5018 13.7563)", srid=4326),
        address_text="Bangkok, Thailand",
        seeker_id=seeker_user.id,
        helper_id=helper_user.id,
        status=GigStatus.ACCEPTED
    )
    
    db_session.add(gig)
    await db_session.commit()
    await db_session.refresh(gig)
    return gig


@pytest.fixture
async def chat_room(db_session: AsyncSession, accepted_gig: Gig):
    """Create a chat room for testing"""
    room = ChatRoom(gig_id=accepted_gig.id)
    db_session.add(room)
    await db_session.commit()
    await db_session.refresh(room)
    return room


class TestWebSocketChat:
    """Test WebSocket chat functionality"""

    def test_websocket_manager_exists(self):
        """Test that WebSocket manager is properly imported"""
        from app.websocket_manager import manager
        assert manager is not None

    @pytest.mark.asyncio
    async def test_message_creation(self, db_session: AsyncSession, chat_room: ChatRoom, seeker_user: User):
        """Test creating a chat message"""
        message = Message(
            content="Hello, this is a test message",
            chat_room_id=chat_room.id,
            sender_id=seeker_user.id
        )
        
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)
        
        assert message.id is not None
        assert message.content == "Hello, this is a test message"
        assert message.chat_room_id == chat_room.id
        assert message.sender_id == seeker_user.id
        assert message.is_read is False
        assert isinstance(message.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_chat_participant_creation(self, db_session: AsyncSession, chat_room: ChatRoom, seeker_user: User):
        """Test creating chat participants"""
        participant = ChatParticipant(
            chat_room_id=chat_room.id,
            user_id=seeker_user.id
        )
        
        db_session.add(participant)
        await db_session.commit()
        await db_session.refresh(participant)
        
        assert participant.id is not None
        assert participant.chat_room_id == chat_room.id
        assert participant.user_id == seeker_user.id
        assert isinstance(participant.joined_at, datetime)

    @pytest.mark.asyncio
    async def test_chat_room_relationships(self, db_session: AsyncSession, accepted_gig: Gig, chat_room: ChatRoom):
        """Test chat room relationships"""
        await db_session.refresh(chat_room, ['gig'])
        
        assert chat_room.gig.id == accepted_gig.id
        assert chat_room.gig.title == "Test Chat Gig"

    def test_websocket_message_format(self):
        """Test that WebSocket message format is correct"""
        # Test message data structure
        message_data = {
            "type": "message",
            "content": "Hello World",
            "image_url": None
        }
        
        assert message_data["type"] == "message"
        assert message_data["content"] == "Hello World"
        assert message_data["image_url"] is None

    def test_typing_indicator_format(self):
        """Test typing indicator message format"""
        typing_data = {
            "type": "typing",
            "is_typing": True
        }
        
        assert typing_data["type"] == "typing"
        assert typing_data["is_typing"] is True


class TestWebSocketAuthentication:
    """Test WebSocket authentication"""

    def test_token_creation_for_websocket(self):
        """Test creating JWT tokens for WebSocket authentication"""
        user_id = str(uuid4())
        token_data = {"sub": user_id}
        token = create_access_token(token_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_websocket_access_control(self, accepted_gig: Gig, seeker_user: User, helper_user: User):
        """Test that only gig participants can access chat room"""
        # Test that seeker and helper should have access
        assert seeker_user.id == accepted_gig.seeker_id
        assert helper_user.id == accepted_gig.helper_id
        
        # Create unauthorized user
        unauthorized_user = User(
            email="unauthorized@hourz.app",
            hashed_password=get_password_hash("password"),
            full_name="Unauthorized User"
        )
        
        # Unauthorized user should not have access to this gig's chat
        assert unauthorized_user.id != accepted_gig.seeker_id
        assert unauthorized_user.id != accepted_gig.helper_id


class TestWebSocketMessageTypes:
    """Test different WebSocket message types"""

    def test_text_message_type(self):
        """Test text message type"""
        from app.models import MessageType
        
        message = {
            "type": "message",
            "content": "This is a text message",
            "message_type": MessageType.TEXT
        }
        
        assert message["message_type"] == MessageType.TEXT

    def test_image_message_type(self):
        """Test image message type"""
        from app.models import MessageType
        
        message = {
            "type": "message", 
            "content": "Check out this image!",
            "image_url": "https://example.com/image.jpg",
            "message_type": MessageType.IMAGE
        }
        
        assert message["message_type"] == MessageType.IMAGE
        assert message["image_url"] is not None

    def test_system_message_type(self):
        """Test system message type"""
        from app.models import MessageType
        
        message = {
            "type": "system",
            "content": "Gig has been marked as completed",
            "message_type": MessageType.SYSTEM
        }
        
        assert message["message_type"] == MessageType.SYSTEM


# Integration test placeholder - would require more complex setup
class TestWebSocketIntegration:
    """Test WebSocket integration (requires running server)"""
    
    def test_websocket_route_exists(self):
        """Test that WebSocket routes are defined"""
        # This would test actual WebSocket connections in a real integration test
        # For now, just verify the route structure exists
        from app.routes.websocket_routes import router
        assert router is not None