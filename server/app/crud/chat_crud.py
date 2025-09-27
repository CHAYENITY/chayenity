"""
CRUD operations for Chat system
"""
from sqlmodel import Session, select, and_, or_, func, desc
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone
from app.models import ChatRoom, Message, ChatParticipant, User, Gig, MessageType
from app.schemas.chat_schema import MessageCreate, ChatRoomCreate


class ChatCRUD:
    """CRUD operations for chat system"""
    
    @staticmethod
    def get_chat_room_by_gig_and_users(
        db: Session, 
        gig_id: UUID, 
        user_ids: List[UUID]
    ) -> Optional[ChatRoom]:
        """
        Find chat room for specific gig with specific participants
        """
        # Get chat room for gig
        stmt = (
            select(ChatRoom)
            .where(ChatRoom.gig_id == gig_id)
        )
        
        chat_room = db.exec(stmt).first()
        if not chat_room:
            return None
        
        # Load participants separately to avoid selectinload issues
        participant_stmt = (
            select(ChatParticipant)
            .where(ChatParticipant.chat_room_id == chat_room.id)
        )
        participants = db.exec(participant_stmt).all()
        
        # Check if participants match
        participant_user_ids = {p.user_id for p in participants}
        if set(user_ids) == participant_user_ids:
            return chat_room
        
        return None
    
    @staticmethod
    def create_chat_room(
        db: Session, 
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
        db.commit()
        db.refresh(chat_room)
        
        # Add participants
        for user_id in participant_user_ids:
            participant = ChatParticipant(
                user_id=user_id,
                chat_room_id=chat_room.id
            )
            db.add(participant)
        
        db.commit()
        return chat_room
    
    @staticmethod
    def get_or_create_chat_room(
        db: Session,
        gig_id: UUID,
        requester_id: UUID,
        gig_owner_id: UUID
    ) -> ChatRoom:
        """
        Get existing chat room or create new one for gig communication
        """
        participant_ids = [requester_id, gig_owner_id]
        
        # Try to find existing room
        existing_room = ChatCRUD.get_chat_room_by_gig_and_users(
            db, gig_id, participant_ids
        )
        
        if existing_room:
            return existing_room
        
        # Create new room
        room_data = ChatRoomCreate(gig_id=gig_id)
        return ChatCRUD.create_chat_room(db, room_data, participant_ids)
    
    @staticmethod
    def get_user_chat_rooms(
        db: Session, 
        user_id: UUID,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get all chat rooms for user with pagination - returns dict data
        """
        offset = (page - 1) * per_page
        
        # Get room IDs for user
        room_stmt = (
            select(ChatRoom.id)
            .join(ChatParticipant)
            .where(
                and_(
                    ChatParticipant.user_id == user_id,
                    ChatRoom.is_active == True
                )
            )
            .order_by(desc(ChatRoom.updated_at))
            .offset(offset)
            .limit(per_page)
        )
        
        room_ids = db.exec(room_stmt).all()
        
        # Get room data manually
        rooms_data = []
        for room_id in room_ids:
            room = db.get(ChatRoom, room_id)
            if room:
                # Get gig info
                gig = db.get(Gig, room.gig_id)
                
                # Get participants
                participant_stmt = select(ChatParticipant).where(
                    ChatParticipant.chat_room_id == room_id
                )
                participants = db.exec(participant_stmt).all()
                
                # Get latest message
                latest_msg_stmt = (
                    select(Message)
                    .where(Message.chat_room_id == room_id)
                    .order_by(desc(Message.timestamp))
                    .limit(1)
                )
                latest_message = db.exec(latest_msg_stmt).first()
                
                # Calculate unread count
                unread_count = ChatCRUD.get_unread_message_count(db, room_id, user_id)
                
                room_data = {
                    "id": room.id,
                    "gig_id": room.gig_id,
                    "gig_title": gig.title if gig else "Unknown Gig",
                    "created_at": room.created_at,
                    "updated_at": room.updated_at,
                    "is_active": room.is_active,
                    "participants": participants,
                    "latest_message": latest_message,
                    "unread_count": unread_count
                }
                rooms_data.append(room_data)
        
        # Get total count - use simple approach
        total = len([
            db.exec(
                select(ChatRoom.id)
                .join(ChatParticipant)
                .where(
                    and_(
                        ChatParticipant.user_id == user_id,
                        ChatRoom.is_active == True
                    )
                )
            ).all()
        ])
        
        return rooms_data, total
    
    @staticmethod
    def get_chat_room_by_id(
        db: Session, 
        room_id: UUID, 
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get chat room by ID if user is participant - returns dict data
        """
        # Check if user is participant
        participant_check = (
            select(ChatParticipant)
            .where(
                and_(
                    ChatParticipant.chat_room_id == room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        
        if not db.exec(participant_check).first():
            return None
        
        # Get room
        room = db.get(ChatRoom, room_id)
        if not room or not room.is_active:
            return None
        
        # Get gig info
        gig = db.get(Gig, room.gig_id)
        
        # Get participants with user info - separate queries to avoid join issues
        participant_stmt = (
            select(ChatParticipant)
            .where(ChatParticipant.chat_room_id == room_id)
        )
        room_participants = db.exec(participant_stmt).all()
        
        participants = []
        for participant in room_participants:
            user = db.get(User, participant.user_id)
            if user:
                participants.append({
                    "id": participant.id,
                    "joined_at": participant.joined_at,
                    "last_read_at": participant.last_read_at,
                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "profile_image_url": user.profile_image_url
                    }
                })
        
        room_data = {
            "id": room.id,
            "gig_id": room.gig_id,
            "gig_title": gig.title if gig else "Unknown Gig",
            "created_at": room.created_at,
            "updated_at": room.updated_at,
            "is_active": room.is_active,
            "participants": participants
        }
        
        return room_data
    
    @staticmethod
    def create_message(
        db: Session,
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
        chat_room = db.get(ChatRoom, chat_room_id)
        if chat_room:
            chat_room.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(message)
        
        # Get sender info
        sender = db.get(User, sender_id)
        
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
    def get_chat_messages(
        db: Session,
        chat_room_id: UUID,
        user_id: UUID,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get messages for chat room with pagination (newest first) - returns dict data
        """
        # Verify user is participant
        participant_check = (
            select(ChatParticipant)
            .where(
                and_(
                    ChatParticipant.chat_room_id == chat_room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        
        if not db.exec(participant_check).first():
            return [], 0
        
        offset = (page - 1) * per_page
        
        # Get messages with sender info - separate queries to avoid join issues
        stmt = (
            select(Message)
            .where(Message.chat_room_id == chat_room_id)
            .order_by(desc(Message.timestamp))
            .offset(offset)
            .limit(per_page)
        )
        
        raw_messages = db.exec(stmt).all()
        
        messages = []
        for message in raw_messages:
            sender = db.get(User, message.sender_id)
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
        
        # Get total count - simple approach
        total_messages = len(
            db.exec(
                select(Message.id)
                .where(Message.chat_room_id == chat_room_id)
            ).all()
        )
        
        return messages, total_messages
    
    @staticmethod
    def get_unread_message_count(
        db: Session,
        chat_room_id: UUID,
        user_id: UUID
    ) -> int:
        """
        Get count of unread messages for user in room
        """
        # Get user's last read time
        participant_stmt = (
            select(ChatParticipant.last_read_at)
            .where(
                and_(
                    ChatParticipant.chat_room_id == chat_room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        
        last_read = db.exec(participant_stmt).first()
        
        if not last_read:
            # If no last read time, count all messages not from user
            stmt = (
                select(func.count())
                .select_from(Message)
                .where(
                    and_(
                        Message.chat_room_id == chat_room_id,
                        Message.sender_id != user_id
                    )
                )
            )
        else:
            # Count messages after last read time, not from user
            stmt = (
                select(func.count())
                .select_from(Message)
                .where(
                    and_(
                        Message.chat_room_id == chat_room_id,
                        Message.sender_id != user_id,
                        Message.timestamp > last_read
                    )
                )
            )
        
        return db.exec(stmt).one()
    
    @staticmethod
    def mark_messages_as_read(
        db: Session,
        chat_room_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Mark all messages as read for user in room
        """
        # Update participant's last read time
        stmt = (
            select(ChatParticipant)
            .where(
                and_(
                    ChatParticipant.chat_room_id == chat_room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        
        participant = db.exec(stmt).first()
        if participant:
            participant.last_read_at = datetime.now(timezone.utc)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_latest_message(db: Session, chat_room_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get latest message in chat room - returns dict data
        """
        # Simple query without join to avoid SQLModel issues
        stmt = (
            select(Message)
            .where(Message.chat_room_id == chat_room_id)
            .order_by(desc(Message.timestamp))
            .limit(1)
        )
        
        message = db.exec(stmt).first()
        if not message:
            return None
        
        # Get sender separately
        sender = db.get(User, message.sender_id)
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
    def delete_chat_room(db: Session, room_id: UUID, user_id: UUID) -> bool:
        """
        Deactivate chat room (soft delete)
        """
        # Verify user is participant
        participant_check = (
            select(ChatParticipant)
            .where(
                and_(
                    ChatParticipant.chat_room_id == room_id,
                    ChatParticipant.user_id == user_id
                )
            )
        )
        
        if not db.exec(participant_check).first():
            return False
        
        # Deactivate room
        chat_room = db.get(ChatRoom, room_id)
        if chat_room:
            chat_room.is_active = False
            db.commit()
            return True
        
        return False