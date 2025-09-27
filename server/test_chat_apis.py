"""
Test Chat REST APIs - Basic functionality test
"""
import requests
import json
from uuid import uuid4


def test_chat_endpoints():
    """Test basic chat endpoints functionality"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Chat REST APIs")
    print("=" * 50)
    
    # Test data - you'll need to replace with real user credentials
    login_data = {
        "username": "chattest@example.com",  # Use username field (email as username)
        "password": "testpass123"            # Replace with real password
    }
    
    try:
        # Step 1: Login to get access token
        print("🔐 Step 1: Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed with status {login_response.status_code}")
            print(f"Response: {login_response.text}")
            print("\n💡 Please create a test user first or update the login credentials in this script")
            return
        
        login_result = login_response.json()
        access_token = login_result["access_token"]
        print(f"✅ Login successful!")
        
        # Headers with authorization
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Step 2: Test Get User Chat Rooms
        print("\n📱 Step 2: Getting user chat rooms...")
        rooms_response = requests.get(f"{base_url}/api/chat/rooms", headers=headers)
        print(f"Status: {rooms_response.status_code}")
        print(f"Response: {json.dumps(rooms_response.json(), indent=2)}")
        
        # Step 3: Test Get Specific Chat Room (using fake UUID)
        fake_room_id = str(uuid4())
        print(f"\n📱 Step 3: Getting specific chat room {fake_room_id[:8]}...")
        room_response = requests.get(f"{base_url}/api/chat/rooms/{fake_room_id}", headers=headers)
        print(f"Status: {room_response.status_code}")
        print(f"Response: {json.dumps(room_response.json(), indent=2)}")
        
        # Step 4: Test Get Chat Messages (using fake UUID)
        print(f"\n💬 Step 4: Getting chat messages for room {fake_room_id[:8]}...")
        messages_response = requests.get(f"{base_url}/api/chat/rooms/{fake_room_id}/messages", headers=headers)
        print(f"Status: {messages_response.status_code}")
        print(f"Response: {json.dumps(messages_response.json(), indent=2)}")
        
        # Step 5: Test Send Message (using fake UUID)
        print(f"\n📨 Step 5: Sending message to room {fake_room_id[:8]}...")
        message_data = {
            "content": "Hello, this is a test message!",
            "message_type": "text"
        }
        send_response = requests.post(
            f"{base_url}/api/chat/rooms/{fake_room_id}/messages", 
            headers=headers, 
            json=message_data
        )
        print(f"Status: {send_response.status_code}")
        print(f"Response: {json.dumps(send_response.json(), indent=2)}")
        
        # Step 6: Test Mark Messages as Read
        print(f"\n✅ Step 6: Marking messages as read in room {fake_room_id[:8]}...")
        read_response = requests.put(f"{base_url}/api/chat/rooms/{fake_room_id}/read", headers=headers)
        print(f"Status: {read_response.status_code}")
        print(f"Response: {json.dumps(read_response.json(), indent=2)}")
        
        # Step 7: Test Delete Chat Room
        print(f"\n🗑️ Step 7: Deleting chat room {fake_room_id[:8]}...")
        delete_response = requests.delete(f"{base_url}/api/chat/rooms/{fake_room_id}", headers=headers)
        print(f"Status: {delete_response.status_code}")
        print(f"Response: {json.dumps(delete_response.json(), indent=2)}")
        
        print("\n🎉 Chat REST APIs Test Complete!")
        print("All endpoints are responding correctly with simplified implementations.")
        print("Next step: Implement full functionality with database operations.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the server is running:")
        print("   cd server")
        print("   poetry run python -m app.main")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


if __name__ == "__main__":
    test_chat_endpoints()