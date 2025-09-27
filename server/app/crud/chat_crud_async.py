"""
Async CRUD operations for Chat system
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, desc, and_
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone
from app.models import ChatRoom, Message, ChatParticipant, User, Gig, MessageType
from app.schemas.chat_schema import MessageCreate, ChatRoomCreate


class ChatCRUD:
    """Async CRUD operations for chat system"""
    
    @staticmethod
    async def get_chat_room_by_gig_and_users(
        db: AsyncSession, 
        gig_id: UUID, 
        user_ids: List[UUID]
    ) -> Optional[ChatRoom]:
        """
        Find chat room for specific gig with specific participants
        """
        # Get chat room for gig
        stmt = select(ChatRoom).where(ChatRoom.gig_id == gig_id)
        result = await db.execute(stmt)
        chat_room = result.scalar_one_or_none()
        
        if not chat_room:
            return None
        
        # Get participants separately
        participant_stmt = select(ChatParticipant).where(
            ChatParticipant.chat_room_id == chat_room.id
        )
        participant_result = await db.execute(participant_stmt)
        participants = participant_result.scalars().all()
        
        # Check if participants match
        participant_user_ids = {p.user_id for p in participants}
        if set(user_ids) == participant_user_ids:
            return chat_room
        
        return None
    
    @staticmethod
    async def create_chat_room(
        db: AsyncSession, 
        chat_data: ChatRoomCreate, 
        participant_user_ids: List[UUID]
    ) -> ChatRoom:
        """
        Create new chat room with participants
        """
        # Create chat room
        chat_room = ChatRoom(
            gig_id=chat_data.gig_id,
            is_active=chat_data.is_active
        )
        
        db.add(chat_room)
        await db.commit()
        await db.refresh(chat_room)
        
        # Add participants
        for user_id in participant_user_ids:
            participant = ChatParticipant(
                user_id=user_id,
                chat_room_id=chat_room.id
            )
            db.add(participant)
        
        await db.commit()
        return chat_room
    
    @staticmethod
    async def get_or_create_chat_room(
        db: AsyncSession,
        gig_id: UUID,
        requester_id: UUID,
        gig_owner_id: UUID
    ) -> ChatRoom:
        """
        Get existing chat room or create new one for gig communication
        """
        participant_ids = [requester_id, gig_owner_id]
        
        # Try to find existing room
        existing_room = await ChatCRUD.get_chat_room_by_gig_and_users(
            db, gig_id, participant_ids
        )
        
        if existing_room:
            return existing_room
        
        # Create new room
        room_data = ChatRoomCreate(gig_id=gig_id)
        return await ChatCRUD.create_chat_room(db, room_data, participant_ids)
    
    @staticmethod
    async def get_user_chat_rooms(
        db: AsyncSession, 
        user_id: UUID,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all chat rooms for user with pagination - returns dict data
        """
        offset = (page - 1) * per_page
        
        # First get participant records for user
        participant_stmt = select(ChatParticipant).where(
            ChatParticipant.user_id == user_id
        )
        participant_result = await db.execute(participant_stmt)
        participants = participant_result.scalars().all()
        
        # Get room IDs
        room_ids = [p.chat_room_id for p in participants]
        
        if not room_ids:
            return [], 0
        
        # Get room data manually for each room (with active filter)
        rooms_data = []
        total_count = 0
        
        for room_id in room_ids:
            # Get room if active
            room_stmt = select(ChatRoom).where(
                and_(
                    ChatRoom.id == room_id,
                    ChatRoom.is_active == True
                )
            )
            room_result = await db.execute(room_stmt)
            room = room_result.scalar_one_or_none()
            
            if room:
                total_count += 1
                # Apply pagination
                if len(rooms_data) >= offset and len(rooms_data) < offset + per_page:
                    room_data = await ChatCRUD._get_room_with_details(db, room.id, user_id)
                    if room_data:
                        rooms_data.append(room_data)
        
        total = total_count
        
        return rooms_data, total
    
    @staticmethod
    async def _get_room_with_details(
        db: AsyncSession, 
        room_id: UUID, 
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Helper method to get room with all details
        """
        # Get room
        room_result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
        room = room_result.scalar_one_or_none()
        if not room:
            return None
        
        # Get gig info
        gig_result = await db.execute(select(Gig).where(Gig.id == room.gig_id))
        gig = gig_result.scalar_one_or_none()
        
        # Get participants
        participant_stmt = select(ChatParticipant).where(
            ChatParticipant.chat_room_id == room_id
        )
        participant_result = await db.execute(participant_stmt)
        participants = participant_result.scalars().all()
        
        # Get participant user details
        participant_details = []
        for participant in participants:
            user_result = await db.execute(select(User).where(User.id == participant.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                participant_details.append({
                    "id": participant.id,
                    "joined_at": participant.joined_at,
                    "last_read_at": participant.last_read_at,
                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "profile_image_url": user.profile_image_url
                    }
                })
        
        # Get latest message
        latest_message = await ChatCRUD.get_latest_message(db, room_id)
        
        # Calculate unread count
        unread_count = await ChatCRUD.get_unread_message_count(db, room_id, user_id)
        
        return {
            "id": room.id,
            "gig_id": room.gig_id,
            "gig_title": gig.title if gig else "Unknown Gig",
            "created_at": room.created_at,
            "updated_at": room.updated_at,
            "is_active": room.is_active,
            "participants": participant_details,
            "latest_message": latest_message,
            "unread_count": unread_count
        }
    
    @staticmethod
    async def get_chat_room_by_id(
        db: AsyncSession, 
        room_id: UUID, 
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get chat room by ID if user is participant - returns dict data
        """
        # Check if user is participant
        participant_check = select(ChatParticipant).where(
            and_(
                ChatParticipant.chat_room_id == room_id,
                ChatParticipant.user_id == user_id
            )
        )
        
        check_result = await db.execute(participant_check)
        if not check_result.scalar_one_or_none():
            return None
        
        return await ChatCRUD._get_room_with_details(db, room_id, user_id)
    
    @staticmethod
    async def create_message(
        db: AsyncSession,
        message_data: MessageCreate,
        sender_id: UUID,
        chat_room_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Create new message in chat room - returns dict data
        """
        message = Message(
            content=message_data.content,
            message_type=message_data.message_type,
            image_url=message_data.image_url,
            sender_id=sender_id,
            chat_room_id=chat_room_id
        )
        
        db.add(message)
        
        # Update chat room timestamp
        room_result = await db.execute(select(ChatRoom).where(ChatRoom.id == chat_room_id))
        chat_room = room_result.scalar_one_or_none()
        if chat_room:
            chat_room.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(message)
        
        # Get sender info
        sender_result = await db.execute(select(User).where(User.id == sender_id))
        sender = sender_result.scalar_one_or_none()
        
        if not sender:
            return None
        
        return {
            "id": message.id,
            "content": message.content,
            "message_type": message.message_type,
            "image_url": message.image_url,
            "timestamp": message.timestamp,
            "is_read": message.is_read,
            "sender_id": message.sender_id,
            "chat_room_id": message.chat_room_id,
            "sender": {
                "id": sender.id,
                "full_name": sender.full_name,
                "profile_image_url": sender.profile_image_url
            }
        }
    
    @staticmethod
    async def get_chat_messages(
        db: AsyncSession,
        chat_room_id: UUID,
        user_id: UUID,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get messages for chat room with pagination (newest first) - returns dict data
        """
        # Verify user is participant
        participant_check = select(ChatParticipant).where(
            and_(
                ChatParticipant.chat_room_id == chat_room_id,
                ChatParticipant.user_id == user_id
            )
        )
        
        check_result = await db.execute(participant_check)
        if not check_result.scalar_one_or_none():
            return [], 0
        
        offset = (page - 1) * per_page
        
        # Get messages
        stmt = (
            select(Message)
            .where(Message.chat_room_id == chat_room_id)
            .order_by(desc(Message.timestamp))
            .offset(offset)
            .limit(per_page)
        )
        
        message_result = await db.execute(stmt)
        raw_messages = message_result.scalars().all()
        
        # Get message details with sender info
        messages = []
        for message in raw_messages:
            sender_result = await db.execute(select(User).where(User.id == message.sender_id))
            sender = sender_result.scalar_one_or_none()
            if sender:
                messages.append({
                    "id": message.id,
                    "content": message.content,
                    "message_type": message.message_type,
                    "image_url": message.image_url,
                    "timestamp": message.timestamp,
                    "is_read": message.is_read,
                    "sender_id": message.sender_id,
                    "chat_room_id": message.chat_room_id,
                    "sender": {
                        "id": sender.id,
                        "full_name": sender.full_name,
                        "profile_image_url": sender.profile_image_url
                    }
                })
        
        # Get total count by counting messages
        count_stmt = select(Message).where(Message.chat_room_id == chat_room_id)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        return messages, total
    
    @staticmethod
    async def get_unread_message_count(
        db: AsyncSession,
        chat_room_id: UUID,
        user_id: UUID
    ) -> int:
        """
        Get count of unread messages for user in room
        """
        # Get user's last read time
        participant_stmt = select(ChatParticipant.last_read_at).where(
            and_(
                ChatParticipant.chat_room_id == chat_room_id,
                ChatParticipant.user_id == user_id
            )
        )
        
        participant_result = await db.execute(participant_stmt)
        last_read = participant_result.scalar_one_or_none()
        
        if not last_read:
            # If no last read time, count all messages not from user
            stmt = select(Message).where(
                and_(
                    Message.chat_room_id == chat_room_id,
                    Message.sender_id != user_id
                )
            )
        else:
            # Count messages after last read time, not from user
            stmt = select(Message).where(
                and_(
                    Message.chat_room_id == chat_room_id,
                    Message.sender_id != user_id,
                    Message.timestamp > last_read
                )
            )
        
        count_result = await db.execute(stmt)
        return len(count_result.scalars().all())
    
    @staticmethod
    async def mark_messages_as_read(
        db: AsyncSession,
        chat_room_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Mark all messages as read for user in room
        """
        # Update participant's last read time
        stmt = select(ChatParticipant).where(
            and_(
                ChatParticipant.chat_room_id == chat_room_id,
                ChatParticipant.user_id == user_id
            )
        )
        
        result = await db.execute(stmt)
        participant = result.scalar_one_or_none()
        if participant:
            participant.last_read_at = datetime.now()
            await db.commit()
            return True
        
        return False
    
    @staticmethod
    async def get_latest_message(
        db: AsyncSession, 
        chat_room_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest message in chat room - returns dict data
        """
        stmt = (
            select(Message)
            .where(Message.chat_room_id == chat_room_id)
            .order_by(desc(Message.timestamp))
            .limit(1)
        )
        
        result = await db.execute(stmt)
        message = result.scalar_one_or_none()
        if not message:
            return None
        
        # Get sender separately
        sender_result = await db.execute(select(User).where(User.id == message.sender_id))
        sender = sender_result.scalar_one_or_none()
        if not sender:
            return None
        
        return {
            "id": message.id,
            "content": message.content,
            "message_type": message.message_type,
            "image_url": message.image_url,
            "timestamp": message.timestamp,
            "is_read": message.is_read,
            "sender_id": message.sender_id,
            "chat_room_id": message.chat_room_id,
            "sender": {
                "id": sender.id,
                "full_name": sender.full_name,
                "profile_image_url": sender.profile_image_url
            }
        }
    
    @staticmethod
    async def delete_chat_room(
        db: AsyncSession, 
        room_id: UUID, 
        user_id: UUID
    ) -> bool:
        """
        Deactivate chat room (soft delete)
        """
        # Verify user is participant
        participant_check = select(ChatParticipant).where(
            and_(
                ChatParticipant.chat_room_id == room_id,
                ChatParticipant.user_id == user_id
            )
        )
        
        check_result = await db.execute(participant_check)
        if not check_result.scalar_one_or_none():
            return False
        
        # Deactivate room
        room_result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_id))
        chat_room = room_result.scalar_one_or_none()
        if chat_room:
            chat_room.is_active = False
            await db.commit()
            return True
        
        return False