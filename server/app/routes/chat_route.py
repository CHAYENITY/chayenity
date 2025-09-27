"""
Chat REST API routes - Full implementation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database.session import get_db
from app.security import get_current_user_with_access_token
from app.models import User
from app.schemas.chat_schema import (
    MessageCreate, MessageOut, ChatRoomSummary, 
    MessageHistoryOut, ChatRoomDetailOut, UserSummary
)
from app.crud.chat_crud_async import ChatCRUD

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/rooms", response_model=List[ChatRoomSummary])
async def get_user_chat_rooms(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_access_token)
):
    """
    Get all chat rooms for current user with pagination
    """
    try:
        print(f"📱 Chat rooms requested by user: {current_user.full_name} (ID: {current_user.id})")
        
        rooms_data, total = await ChatCRUD.get_user_chat_rooms(
            db, current_user.id, page, per_page
        )
        
        # Convert to response format
        chat_rooms = []
        for room_data in rooms_data:
            # Convert participants
            participants = []
            for p_data in room_data["participants"]:
                participants.append(UserSummary(
                    id=p_data["user"]["id"],
                    full_name=p_data["user"]["full_name"],
                    profile_image_url=p_data["user"]["profile_image_url"]
                ))
            
            # Convert latest message if exists
            latest_message = None
            if room_data["latest_message"]:
                msg = room_data["latest_message"]
                latest_message = MessageOut(
                    id=msg["id"],
                    content=msg["content"],
                    message_type=msg["message_type"],
                    image_url=msg["image_url"],
                    timestamp=msg["timestamp"],
                    is_read=msg["is_read"],
                    sender_id=msg["sender_id"],
                    chat_room_id=msg["chat_room_id"],
                    sender=UserSummary(
                        id=msg["sender"]["id"],
                        full_name=msg["sender"]["full_name"],
                        profile_image_url=msg["sender"]["profile_image_url"]
                    )
                )
            
            room_summary = ChatRoomSummary(
                id=room_data["id"],
                gig_id=room_data["gig_id"],
                gig_title=room_data["gig_title"],
                created_at=room_data["created_at"],
                is_active=room_data["is_active"],
                participants=participants,
                latest_message=latest_message,
                unread_count=room_data["unread_count"]
            )
            chat_rooms.append(room_summary)
        
        print(f"✅ Found {len(chat_rooms)} chat rooms for user {current_user.full_name}")
        return chat_rooms
    
    except Exception as e:
        print(f"❌ Error getting user chat rooms: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat rooms")


@router.get("/rooms/{room_id}", response_model=ChatRoomDetailOut)
async def get_chat_room(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_access_token)
):
    """
    Get specific chat room details if user is participant
    """
    try:
        print(f"📱 Chat room {room_id} requested by user: {current_user.full_name}")
        
        room_data = await ChatCRUD.get_chat_room_by_id(db, room_id, current_user.id)
        
        if not room_data:
            raise HTTPException(
                status_code=404, 
                detail="Chat room not found or access denied"
            )
        
        # Get recent messages (last 20)
        recent_messages_data, _ = await ChatCRUD.get_chat_messages(
            db, room_id, current_user.id, page=1, per_page=20
        )
        
        # Convert recent messages
        recent_messages = []
        for msg_data in recent_messages_data:
            recent_messages.append(MessageOut(
                id=msg_data["id"],
                content=msg_data["content"],
                message_type=msg_data["message_type"],
                image_url=msg_data["image_url"],
                timestamp=msg_data["timestamp"],
                is_read=msg_data["is_read"],
                sender_id=msg_data["sender_id"],
                chat_room_id=msg_data["chat_room_id"],
                sender=UserSummary(
                    id=msg_data["sender"]["id"],
                    full_name=msg_data["sender"]["full_name"],
                    profile_image_url=msg_data["sender"]["profile_image_url"]
                )
            ))
        
        # Convert participants
        participants = []
        for p_data in room_data["participants"]:
            participants.append({
                "id": p_data["id"],
                "joined_at": p_data["joined_at"],
                "last_read_at": p_data["last_read_at"],
                "user": UserSummary(
                    id=p_data["user"]["id"],
                    full_name=p_data["user"]["full_name"],
                    profile_image_url=p_data["user"]["profile_image_url"]
                )
            })
        
        room_detail = ChatRoomDetailOut(
            id=room_data["id"],
            gig_id=room_data["gig_id"],
            created_at=room_data["created_at"],
            updated_at=room_data["updated_at"],
            is_active=room_data["is_active"],
            participants=participants,
            recent_messages=recent_messages,
            unread_count=room_data["unread_count"]
        )
        
        print(f"✅ Chat room {room_id} retrieved for user {current_user.full_name}")
        return room_detail
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting chat room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat room")


@router.get("/rooms/{room_id}/messages", response_model=MessageHistoryOut)
async def get_chat_messages(
    room_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Messages per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_access_token)
):
    """
    Get message history for chat room with pagination (newest first)
    """
    try:
        print(f"📱 Messages for room {room_id} requested by user: {current_user.full_name}")
        
        messages_data, total = await ChatCRUD.get_chat_messages(
            db, room_id, current_user.id, page, per_page
        )
        
        if not messages_data and page == 1:
            # Check if room exists and user has access
            room_data = await ChatCRUD.get_chat_room_by_id(db, room_id, current_user.id)
            if not room_data:
                raise HTTPException(
                    status_code=404, 
                    detail="Chat room not found or access denied"
                )
        
        # Convert to response format
        messages = []
        for msg_data in messages_data:
            messages.append(MessageOut(
                id=msg_data["id"],
                content=msg_data["content"],
                message_type=msg_data["message_type"],
                image_url=msg_data["image_url"],
                timestamp=msg_data["timestamp"],
                is_read=msg_data["is_read"],
                sender_id=msg_data["sender_id"],
                chat_room_id=msg_data["chat_room_id"],
                sender=UserSummary(
                    id=msg_data["sender"]["id"],
                    full_name=msg_data["sender"]["full_name"],
                    profile_image_url=msg_data["sender"]["profile_image_url"]
                )
            ))
        
        has_next = (page * per_page) < total
        has_prev = page > 1
        
        result = MessageHistoryOut(
            messages=messages,
            total_count=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
        print(f"✅ Retrieved {len(messages)} messages for room {room_id}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting messages for room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")


@router.post("/rooms/{room_id}/messages", response_model=MessageOut)
async def send_message(
    room_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_access_token)
):
    """
    Send message to chat room
    """
    try:
        print(f"📱 Message sent to room {room_id} by user: {current_user.full_name}")
        print(f"📨 Message content: {message_data.content}")
        
        # Verify user has access to room
        room_data = await ChatCRUD.get_chat_room_by_id(db, room_id, current_user.id)
        if not room_data:
            raise HTTPException(
                status_code=404, 
                detail="Chat room not found or access denied"
            )
        
        # Create message
        message_result = await ChatCRUD.create_message(
            db, message_data, current_user.id, room_id
        )
        
        if not message_result:
            raise HTTPException(status_code=500, detail="Failed to create message")
        
        # Convert to response format
        message_out = MessageOut(
            id=message_result["id"],
            content=message_result["content"],
            message_type=message_result["message_type"],
            image_url=message_result["image_url"],
            timestamp=message_result["timestamp"],
            is_read=message_result["is_read"],
            sender_id=message_result["sender_id"],
            chat_room_id=message_result["chat_room_id"],
            sender=UserSummary(
                id=message_result["sender"]["id"],
                full_name=message_result["sender"]["full_name"],
                profile_image_url=message_result["sender"]["profile_image_url"]
            )
        )
        
        print(f"✅ Message sent to room {room_id} by user {current_user.full_name}")
        return message_out
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error sending message to room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.put("/rooms/{room_id}/read")
async def mark_messages_as_read(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_access_token)
):
    """
    Mark all messages in room as read for current user
    """
    try:
        print(f"📱 Messages marked as read in room {room_id} by user: {current_user.full_name}")
        
        success = await ChatCRUD.mark_messages_as_read(db, room_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Chat room not found or access denied"
            )
        
        return {
            "message": "Messages marked as read",
            "room_id": str(room_id),
            "user_id": str(current_user.id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error marking messages as read for room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark messages as read")


@router.delete("/rooms/{room_id}")
async def delete_chat_room(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_access_token)
):
    """
    Deactivate chat room (soft delete)
    """
    try:
        print(f"📱 Chat room {room_id} deleted by user: {current_user.full_name}")
        
        success = await ChatCRUD.delete_chat_room(db, room_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Chat room not found or access denied"
            )
        
        return {
            "message": "Chat room deleted successfully",
            "room_id": str(room_id),
            "user_id": str(current_user.id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting chat room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat room")