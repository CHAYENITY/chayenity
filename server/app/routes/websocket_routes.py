"""
WebSocket endpoints for real-time chat in Hourz app
"""
import json
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.websocket_manager import manager
from app.database.session import get_db
from app.models import User, ChatRoom, Gig, GigStatus
from app.security import decode_access_token

router = APIRouter()


async def get_user_from_token(token: str, db: AsyncSession) -> User:
    """Authenticate user from JWT token for WebSocket"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.get(User, UUID(user_id))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for chat rooms"""
    try:
        # Authenticate user
        user = await get_user_from_token(token, db)
        
        # Verify user has access to this chat room
        chat_room = await db.get(ChatRoom, UUID(room_id))
        if not chat_room:
            await websocket.close(code=4004, reason="Chat room not found")
            return
        
        # Check if user is participant (seeker or helper of the gig)
        gig = chat_room.gig
        if user.id not in (gig.seeker_id, gig.helper_id):
            await websocket.close(code=4003, reason="Access denied")
            return
        
        # Connect to chat room
        await manager.connect(websocket, room_id, user.id)
        
        try:
            while True:
                # Receive message from WebSocket
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                message_type = message_data.get("type", "message")
                
                if message_type == "message":
                    content = message_data.get("content", "")
                    image_url = message_data.get("image_url")
                    
                    if content.strip() or image_url:
                        # Save and broadcast message
                        await manager.save_and_broadcast_message(
                            room_id=room_id,
                            sender_id=user.id,
                            content=content,
                            image_url=image_url
                        )
                
                elif message_type == "typing":
                    # Broadcast typing indicator
                    await manager.broadcast_to_room(room_id, {
                        "type": "typing",
                        "user_id": str(user.id),
                        "user_name": user.full_name,
                        "is_typing": message_data.get("is_typing", False)
                    }, exclude_websocket=websocket)
                
        except WebSocketDisconnect:
            await manager.disconnect(websocket, room_id)
        except Exception as e:
            print(f"WebSocket error: {e}")
            await manager.disconnect(websocket, room_id)
    
    except HTTPException:
        await websocket.close(code=4001, reason="Authentication failed")
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        await websocket.close(code=4000, reason="Connection error")