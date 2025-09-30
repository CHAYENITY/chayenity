"""
WebSocket connection manager for real-time chat in Hourz app
"""
import json
from typing import Dict, List, Set, Optional
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
from app.models import User, ChatRoom, Message, MessageType
from app.database.session import AsyncSessionLocal


class ConnectionManager:
    def __init__(self):
        # Room ID -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # WebSocket -> User ID mapping for authentication
        self.connection_users: Dict[WebSocket, UUID] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: UUID):
        """Accept WebSocket connection and add to room"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        self.connection_users[websocket] = user_id
        
        # Notify room that user joined
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": str(user_id),
            "message": "User joined the chat"
        }, exclude_websocket=websocket)

    async def disconnect(self, websocket: WebSocket, room_id: str):
        """Remove WebSocket connection from room"""
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        user_id = self.connection_users.pop(websocket, None)
        if user_id:
            # Notify room that user left
            await self.broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": str(user_id),
                "message": "User left the chat"
            })

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            # Connection might be closed
            pass

    async def broadcast_to_room(self, room_id: str, message: dict, exclude_websocket: Optional[WebSocket] = None):
        """Send message to all connections in a room"""
        if room_id not in self.active_connections:
            return
        
        disconnected_websockets = []
        message_text = json.dumps(message)
        
        for websocket in self.active_connections[room_id]:
            if websocket == exclude_websocket:
                continue
                
            try:
                await websocket.send_text(message_text)
            except Exception:
                # Connection is closed, mark for removal
                disconnected_websockets.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket, room_id)

    async def save_and_broadcast_message(
        self, 
        room_id: str, 
        sender_id: UUID, 
        content: str, 
        message_type: MessageType = MessageType.TEXT,
        image_url: Optional[str] = None
    ):
        """Save message to database and broadcast to room"""
        async with AsyncSessionLocal() as db:
            # Create and save message
            message = Message(
                chat_room_id=UUID(room_id),
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                image_url=image_url
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            # Get sender info for broadcast
            sender = await db.get(User, sender_id)
            
            # Broadcast message to room
            await self.broadcast_to_room(room_id, {
                "type": "message",
                "message_id": str(message.id),
                "sender_id": str(sender_id),
                "sender_name": sender.full_name if sender else "Unknown",
                "content": content,
                "message_type": message_type.value,
                "image_url": image_url,
                "timestamp": message.timestamp.isoformat()
            })
            
            return message

    def get_room_connections_count(self, room_id: str) -> int:
        """Get number of active connections in a room"""
        return len(self.active_connections.get(room_id, set()))


# Global connection manager instance
manager = ConnectionManager()