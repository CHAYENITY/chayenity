"""
Chat Room Functionality Integration Tests

This module tests the complete chat room functionality including:
- Chat room creation and management
- Real-time messaging workflows
- WebSocket integration testing
- Message history and persistence
- Multi-user chat scenarios
- File sharing in chat
- Chat room permissions and security
"""

import pytest
import asyncio
import websockets
import json
from io import BytesIO
import uuid
from fastapi.testclient import TestClient
from app.main import app


def create_authenticated_client(email: str, password: str, full_name: str = "Test User"):
    """Create an authenticated test client"""
    client = TestClient(app)
    
    # Register user (ignore if already exists)
    register_data = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    client.post("/api/auth/register", json=register_data)
    
    # Login to get token
    login_resp = client.post("/api/auth/login", data={
        "username": email,
        "password": password
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    
    token = login_resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    return client


class TestChatRoomFunctionality:
    """Test comprehensive chat room functionality"""

    def test_chat_room_creation_through_gig_acceptance(self):
        """Test that chat rooms are automatically created when gigs are accepted"""
        
        # Create authenticated clients
        user1_client = create_authenticated_client("chatuser1@example.com", "chatpass123", "Chat User One")
        user2_client = create_authenticated_client("chatuser2@example.com", "chatpass123", "Chat User Two")
        
        # Set locations
        user1_client.put("/api/users/location", json={"latitude": 13.7563, "longitude": 100.5018})
        user2_client.put("/api/users/location", json={"latitude": 13.7563, "longitude": 100.5018})
        user2_client.put("/api/users/availability", json={"is_available": True})
        
        # User 1 creates a gig
        gig_data = {
            "title": "Test chat room creation",
            "description": "This gig tests chat room auto-creation",
            "budget": 100.0,
            "duration_hours": 1,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = user1_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        # Verify no chat rooms exist initially
        rooms_resp1 = user1_client.get("/api/chat/rooms")
        assert rooms_resp1.status_code == 200
        initial_rooms = rooms_resp1.json()
        initial_count = len(initial_rooms)
        
        # User 2 accepts the gig
        accept_resp = user2_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Verify chat room was created for both users
        rooms_resp1 = user1_client.get("/api/chat/rooms")
        assert rooms_resp1.status_code == 200
        user1_rooms = rooms_resp1.json()
        assert len(user1_rooms) == initial_count + 1
        
        rooms_resp2 = user2_client.get("/api/chat/rooms")
        assert rooms_resp2.status_code == 200
        user2_rooms = rooms_resp2.json()
        
        # Both users should see the same chat room
        gig_room_user1 = next((room for room in user1_rooms if room["gig_id"] == gig_id), None)
        gig_room_user2 = next((room for room in user2_rooms if room["gig_id"] == gig_id), None)
        
        assert gig_room_user1 is not None
        assert gig_room_user2 is not None
        assert gig_room_user1["id"] == gig_room_user2["id"]
        
        return gig_room_user1["id"], user1_client, user2_client

    def test_comprehensive_messaging_workflow(self):
        """Test complete messaging workflow between users"""
        
        # Create gig and get chat room
        room_id, user1_client, user2_client = self.test_chat_room_creation_through_gig_acceptance()
        
        # Test text messaging
        messages_to_send = [
            {
                "sender": user1_client,
                "content": "Hello! I'm the gig seeker.",
                "message_type": "text"
            },
            {
                "sender": user2_client,
                "content": "Hi there! I accepted your gig. When should we start?",
                "message_type": "text"
            },
            {
                "sender": user1_client,
                "content": "How about tomorrow at 2 PM?",
                "message_type": "text"
            },
            {
                "sender": user2_client,
                "content": "Perfect! I'll see you then.",
                "message_type": "text"
            }
        ]
        
        sent_message_ids = []
        
        # Send all messages
        for msg_data in messages_to_send:
            resp = msg_data["sender"].post(f"/api/chat/rooms/{room_id}/messages", 
                                         json={
                                             "content": msg_data["content"],
                                             "message_type": msg_data["message_type"]
                                         })
            assert resp.status_code == 201, f"Failed to send message: {resp.text}"
            message = resp.json()
            sent_message_ids.append(message["id"])
        
        # Verify message history for both users
        history_resp1 = user1_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert history_resp1.status_code == 200
        messages1 = history_resp1.json()
        
        history_resp2 = user2_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert history_resp2.status_code == 200
        messages2 = history_resp2.json()
        
        # Both users should see the same messages
        assert len(messages1) >= len(messages_to_send)
        assert len(messages2) >= len(messages_to_send)
        
        # Verify message content and order
        recent_messages = messages1[-len(messages_to_send):]
        for i, sent_msg in enumerate(messages_to_send):
            assert recent_messages[i]["content"] == sent_msg["content"]
            assert recent_messages[i]["message_type"] == sent_msg["message_type"]
        
        # Test message read status
        read_resp = user2_client.put(f"/api/chat/rooms/{room_id}/read")
        assert read_resp.status_code == 200

    def test_chat_room_permissions_and_security(self):
        """Test chat room access permissions and security"""
        
        # Create gig and chat room between user1 and user2
        room_id, user1_client, user2_client = self.test_chat_room_creation_through_gig_acceptance()
        
        # Create third user who shouldn't have access
        user3_client = create_authenticated_client("unauthorizeduser@example.com", "password123", "Unauthorized User")
        
        # User3 tries to access chat room (should fail)
        unauthorized_resp = user3_client.get(f"/api/chat/rooms/{room_id}")
        assert unauthorized_resp.status_code == 403, "Unauthorized user should not access chat room"
        
        # User3 tries to send message (should fail)
        message_data = {
            "content": "I shouldn't be able to send this",
            "message_type": "text"
        }
        unauthorized_msg_resp = user3_client.post(f"/api/chat/rooms/{room_id}/messages", 
                                                 json=message_data)
        assert unauthorized_msg_resp.status_code == 403, "Unauthorized user should not send messages"
        
        # User3 tries to get message history (should fail)
        unauthorized_history_resp = user3_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert unauthorized_history_resp.status_code == 403, "Unauthorized user should not access messages"

    def test_chat_room_image_sharing(self):
        """Test image sharing functionality in chat rooms"""
        
        # Create chat room
        room_id, user1_client, user2_client = self.test_chat_room_creation_through_gig_acceptance()
        
        # User1 uploads an image
        image_content = b"fake_image_content_for_chat_testing"
        files = {"file": ("chat_image.jpg", BytesIO(image_content), "image/jpeg")}
        
        upload_resp = user1_client.post("/api/upload/general", files=files)
        assert upload_resp.status_code == 201, f"Failed to upload image: {upload_resp.text}"
        uploaded_file = upload_resp.json()
        image_url = f"/api/upload/{uploaded_file['id']}"
        
        # Send message with image
        image_message_data = {
            "content": "Here's the image you requested",
            "message_type": "image",
            "image_url": image_url
        }
        
        image_msg_resp = user1_client.post(f"/api/chat/rooms/{room_id}/messages", 
                                          json=image_message_data)
        assert image_msg_resp.status_code == 201, f"Failed to send image message: {image_msg_resp.text}"
        
        # User2 receives and views the image message
        history_resp = user2_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert history_resp.status_code == 200
        messages = history_resp.json()
        
        image_message = next((msg for msg in messages if msg["message_type"] == "image"), None)
        assert image_message is not None, "Image message not found in history"
        assert image_message["image_url"] == image_url
        
        # User2 can access the shared image
        image_resp = user2_client.get(image_url)
        assert image_resp.status_code == 200
        assert image_resp.headers["content-type"] == "image/jpeg"

    def test_chat_room_message_pagination(self):
        """Test message pagination in chat rooms"""
        
        # Create chat room
        room_id, user1_client, user2_client = self.test_chat_room_creation_through_gig_acceptance()
        
        # Send many messages to test pagination
        num_messages = 15
        sent_messages = []
        
        for i in range(num_messages):
            message_data = {
                "content": f"Test message number {i + 1}",
                "message_type": "text"
            }
            
            sender = user1_client if i % 2 == 0 else user2_client
            resp = sender.post(f"/api/chat/rooms/{room_id}/messages", json=message_data)
            assert resp.status_code == 201
            sent_messages.append(message_data["content"])
        
        # Test pagination - get first page
        page1_resp = user1_client.get(f"/api/chat/rooms/{room_id}/messages?limit=10&offset=0")
        assert page1_resp.status_code == 200
        page1_messages = page1_resp.json()
        
        # Test pagination - get second page
        page2_resp = user1_client.get(f"/api/chat/rooms/{room_id}/messages?limit=10&offset=10")
        assert page2_resp.status_code == 200
        page2_messages = page2_resp.json()
        
        # Verify pagination works correctly
        assert len(page1_messages) == 10
        assert len(page2_messages) >= 5  # At least the remaining messages
        
        # Verify no duplicate messages between pages
        page1_ids = {msg["id"] for msg in page1_messages}
        page2_ids = {msg["id"] for msg in page2_messages}
        assert page1_ids.isdisjoint(page2_ids), "Pages should not have overlapping messages"

    def test_chat_room_deletion_and_deactivation(self):
        """Test chat room deletion and deactivation"""
        
        # Create chat room
        room_id, user1_client, user2_client = self.test_chat_room_creation_through_gig_acceptance()
        
        # Send some messages
        message_data = {
            "content": "This message will be in a deleted room",
            "message_type": "text"
        }
        
        msg_resp = user1_client.post(f"/api/chat/rooms/{room_id}/messages", json=message_data)
        assert msg_resp.status_code == 201
        
        # User1 deletes/deactivates the chat room
        delete_resp = user1_client.delete(f"/api/chat/rooms/{room_id}")
        assert delete_resp.status_code == 200
        
        # Verify room is no longer accessible
        room_resp = user1_client.get(f"/api/chat/rooms/{room_id}")
        assert room_resp.status_code == 404, "Deleted room should not be accessible"
        
        # Verify room doesn't appear in room list
        rooms_resp = user1_client.get("/api/chat/rooms")
        assert rooms_resp.status_code == 200
        rooms = rooms_resp.json()
        
        room_ids = [room["id"] for room in rooms]
        assert room_id not in room_ids, "Deleted room should not appear in room list"

    def test_multiple_concurrent_chat_rooms(self):
        """Test managing multiple concurrent chat rooms"""
        
        # Create authenticated clients
        user1_client = create_authenticated_client("multichatuser1@example.com", "chatpass123", "Multi Chat User One")
        user2_client = create_authenticated_client("multichatuser2@example.com", "chatpass123", "Multi Chat User Two")
        
        # Set locations
        user1_client.put("/api/users/location", json={"latitude": 13.7563, "longitude": 100.5018})
        user2_client.put("/api/users/location", json={"latitude": 13.7563, "longitude": 100.5018})
        user2_client.put("/api/users/availability", json={"is_available": True})
        
        # Create multiple gigs and chat rooms
        gig_data_list = [
            {
                "title": "First gig for chat testing",
                "description": "Testing multiple chat rooms",
                "budget": 100.0,
                "duration_hours": 1,
                "latitude": 13.7563,
                "longitude": 100.5018
            },
            {
                "title": "Second gig for chat testing", 
                "description": "Testing multiple chat rooms again",
                "budget": 200.0,
                "duration_hours": 2,
                "latitude": 13.7563,
                "longitude": 100.5018
            }
        ]
        
        room_ids = []
        gig_ids = []
        
        # Create multiple gigs and accept them
        for gig_data in gig_data_list:
            # User1 creates gig
            create_resp = user1_client.post("/api/gigs", json=gig_data)
            assert create_resp.status_code == 201
            gig_id = create_resp.json()["id"]
            gig_ids.append(gig_id)
            
            # User2 accepts gig
            accept_resp = user2_client.post(f"/api/gigs/{gig_id}/accept")
            assert accept_resp.status_code == 200
        
        # Get all chat rooms
        rooms_resp = user1_client.get("/api/chat/rooms")
        assert rooms_resp.status_code == 200
        rooms = rooms_resp.json()
        
        # Find rooms for our gigs
        gig_rooms = [room for room in rooms if room["gig_id"] in gig_ids]
        assert len(gig_rooms) == len(gig_data_list), "Should have chat room for each gig"
        
        # Send different messages in each room
        for i, room in enumerate(gig_rooms):
            room_id = room["id"]
            message_data = {
                "content": f"Message for gig {i + 1}: {gig_data_list[i]['title']}",
                "message_type": "text"
            }
            
            msg_resp = user1_client.post(f"/api/chat/rooms/{room_id}/messages", 
                                        json=message_data)
            assert msg_resp.status_code == 201
        
        # Verify messages are in correct rooms
        for i, room in enumerate(gig_rooms):
            room_id = room["id"]
            history_resp = user1_client.get(f"/api/chat/rooms/{room_id}/messages")
            assert history_resp.status_code == 200
            messages = history_resp.json()
            
            # Find our test message
            test_message = next((msg for msg in messages 
                               if f"Message for gig {i + 1}" in msg["content"]), None)
            assert test_message is not None, f"Test message not found in room {room_id}"

    def test_chat_room_real_time_message_ordering(self):
        """Test that messages maintain proper chronological order"""
        
        # Create chat room
        room_id, user1_client, user2_client = self.test_chat_room_creation_through_gig_acceptance()
        
        # Send messages rapidly from both users
        import time
        
        messages_sequence = [
            (user1_client, "First message from user1"),
            (user2_client, "First response from user2"),
            (user1_client, "Second message from user1"),
            (user2_client, "Second response from user2"),
            (user1_client, "Third message from user1"),
            (user2_client, "Final response from user2")
        ]
        
        sent_times = []
        
        for sender, content in messages_sequence:
            message_data = {
                "content": content,
                "message_type": "text"
            }
            
            before_send = time.time()
            resp = sender.post(f"/api/chat/rooms/{room_id}/messages", json=message_data)
            after_send = time.time()
            
            assert resp.status_code == 201
            sent_times.append((before_send, after_send, content))
            time.sleep(0.1)  # Small delay to ensure ordering
        
        # Get message history and verify chronological order
        history_resp = user1_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert history_resp.status_code == 200
        messages = history_resp.json()
        
        # Find our test messages and verify they're in correct order
        # messages_sequence is a list of (sender, content) tuples — unpack accordingly
        test_messages = [msg for msg in messages if any(content in msg["content"] for _, content in messages_sequence)]
        
        assert len(test_messages) == len(messages_sequence)
        
        # Verify chronological order by timestamp
        for i in range(len(test_messages) - 1):
            current_time = test_messages[i]["timestamp"]
            next_time = test_messages[i + 1]["timestamp"]
            assert current_time <= next_time, "Messages should be in chronological order"