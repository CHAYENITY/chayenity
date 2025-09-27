"""
Chat system schemas for REST API endpoints
"""
from sqlmodel import SQLModel
from pydantic import field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models import MessageType


# Base schemas
class MessageBase(SQLModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    image_url: Optional[str] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Message content cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message content cannot exceed 1000 characters")
        return v.strip()


class ChatRoomBase(SQLModel):
    is_active: bool = True


# Request schemas
class MessageCreate(MessageBase):
    pass


class ChatRoomCreate(ChatRoomBase):
    gig_id: UUID


# Response schemas
class UserSummary(SQLModel):
    """Simplified user info for chat contexts"""
    id: UUID
    full_name: str
    profile_image_url: Optional[str] = None


class MessageOut(MessageBase):
    id: UUID
    timestamp: datetime
    is_read: bool
    sender_id: UUID
    chat_room_id: UUID
    sender: UserSummary


class ChatParticipantOut(SQLModel):
    id: UUID
    joined_at: datetime
    last_read_at: Optional[datetime] = None
    user: UserSummary


class ChatRoomOut(ChatRoomBase):
    id: UUID
    gig_id: UUID
    created_at: datetime
    updated_at: datetime
    participants: List[ChatParticipantOut] = []
    latest_message: Optional[MessageOut] = None
    unread_count: int = 0


class ChatRoomDetailOut(ChatRoomOut):
    """Extended chat room info with recent messages"""
    recent_messages: List[MessageOut] = []


class MessageHistoryOut(SQLModel):
    """Paginated message history response"""
    messages: List[MessageOut]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Chat room summary for listing user's chats
class ChatRoomSummary(SQLModel):
    id: UUID
    gig_id: UUID
    gig_title: str
    created_at: datetime
    is_active: bool
    participants: List[UserSummary]
    latest_message: Optional[MessageOut] = None
    unread_count: int = 0


# WebSocket message schemas
class WebSocketMessage(SQLModel):
    type: str
    room_id: str
    data: dict


class WebSocketChatMessage(SQLModel):
    type: str = "chat_message"
    room_id: str
    message: MessageOut


class WebSocketUserEvent(SQLModel):
    type: str  # "user_joined" or "user_left"
    room_id: str
    user_id: str
    message: str