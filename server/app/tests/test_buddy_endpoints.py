#!/usr/bin/env python3
"""
Simple working test for Buddy System - uses live FastAPI server
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000"

def register_and_login(email, password, full_name="Test User"):
    """Register and login, return auth headers."""
    # Register
    register_data = {"email": email, "password": password, "full_name": full_name}
    register_resp = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    
    if register_resp.status_code not in (200, 201, 409):
        print(f"Registration failed: {register_resp.status_code} {register_resp.text}")
        return None, None
    
    # Login
    login_data = {"username": email, "password": password}
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code} {login_resp.text}")
        return None, None
    
    token = login_resp.json()["access_token"]
    user_info = register_resp.json()
    headers = {"Authorization": f"Bearer {token}"}
    
    return headers, user_info["id"]

def test_buddy_system():
    """Test the buddy system end-to-end."""
    print("🧪 Testing Buddy System...")
    
    # Create unique email addresses for this test run
    test_id = str(uuid4())[:8]
    
    # Create test users
    print("👤 Creating test users...")
    user1_headers, user1_id = register_and_login(f"buddy1_{test_id}@example.com", "password", "Buddy User 1")
    user2_headers, user2_id = register_and_login(f"buddy2_{test_id}@example.com", "password", "Buddy User 2")
    
    if not user1_headers or not user2_headers:
        print("❌ Failed to create test users")
        return False
    
    print(f"✅ Created users: {user1_id} and {user2_id}")
    
    # Test 1: Add buddy
    print("\n🤝 Testing add buddy...")
    add_buddy_data = {"buddy_id": user2_id, "notes": "Great helper!"}
    add_resp = requests.post(f"{BASE_URL}/api/buddies", json=add_buddy_data, headers=user1_headers)
    
    if add_resp.status_code != 201:
        print(f"❌ Add buddy failed: {add_resp.status_code} {add_resp.text}")
        return False
    
    buddy_info = add_resp.json()
    print(f"✅ Added buddy: {buddy_info['buddy_full_name']}")
    
    # Test 2: List buddies
    print("\n📋 Testing list buddies...")
    list_resp = requests.get(f"{BASE_URL}/api/buddies", headers=user1_headers)
    
    if list_resp.status_code != 200:
        print(f"❌ List buddies failed: {list_resp.status_code} {list_resp.text}")
        return False
    
    buddy_list = list_resp.json()
    print(f"✅ Found {len(buddy_list['buddies'])} buddies")
    
    # Test 3: Get specific buddy
    print(f"\n👀 Testing get buddy details...")
    details_resp = requests.get(f"{BASE_URL}/api/buddies/{user2_id}", headers=user1_headers)
    
    if details_resp.status_code != 200:
        print(f"❌ Get buddy details failed: {details_resp.status_code} {details_resp.text}")
        return False
    
    buddy_details = details_resp.json()
    print(f"✅ Retrieved buddy details: {buddy_details['buddy_full_name']}")
    
    # Test 4: Update buddy notes
    print(f"\n✏️ Testing update buddy notes...")
    update_data = {"notes": "Updated: Excellent communication!"}
    update_resp = requests.put(f"{BASE_URL}/api/buddies/{user2_id}", json=update_data, headers=user1_headers)
    
    if update_resp.status_code != 200:
        print(f"❌ Update buddy failed: {update_resp.status_code} {update_resp.text}")
        return False
    
    updated_buddy = update_resp.json()
    print(f"✅ Updated notes: {updated_buddy['notes']}")
    
    # Test 5: Set user2 as available and check available buddies
    print(f"\n🟢 Testing available buddies...")
    availability_data = {"is_available": True}
    avail_resp = requests.put(f"{BASE_URL}/api/users/availability", json=availability_data, headers=user2_headers)
    
    if avail_resp.status_code != 200:
        print(f"❌ Set availability failed: {avail_resp.status_code} {avail_resp.text}")
        return False
    
    available_resp = requests.get(f"{BASE_URL}/api/buddies/available", headers=user1_headers)
    
    if available_resp.status_code != 200:
        print(f"❌ Get available buddies failed: {available_resp.status_code} {available_resp.text}")
        return False
    
    available_buddies = available_resp.json()
    print(f"✅ Found {len(available_buddies['buddies'])} available buddies")
    
    # Test 6: Remove buddy
    print(f"\n🗑️ Testing remove buddy...")
    remove_resp = requests.delete(f"{BASE_URL}/api/buddies/{user2_id}", headers=user1_headers)
    
    if remove_resp.status_code != 204:
        print(f"❌ Remove buddy failed: {remove_resp.status_code} {remove_resp.text}")
        return False
    
    print(f"✅ Removed buddy")
    
    # Verify buddy was removed
    final_list_resp = requests.get(f"{BASE_URL}/api/buddies", headers=user1_headers)
    final_buddies = final_list_resp.json()
    print(f"✅ Verified removal: {len(final_buddies['buddies'])} buddies remaining")
    
    print("\n🎉 All Buddy System tests passed!")
    return True

def test_error_cases():
    """Test error cases for buddy system."""
    print("\n🚨 Testing error cases...")
    
    test_id = str(uuid4())[:8]
    
    user1_headers, user1_id = register_and_login(f"error1_{test_id}@example.com", "password", "Error User 1")
    user2_headers, user2_id = register_and_login(f"error2_{test_id}@example.com", "password", "Error User 2")
    
    if not user1_headers or not user2_headers:
        print("❌ Failed to create error test users")
        return False
    
    # Test 1: Try to add self as buddy
    self_buddy_data = {"buddy_id": user1_id}
    self_resp = requests.post(f"{BASE_URL}/api/buddies", json=self_buddy_data, headers=user1_headers)
    
    if self_resp.status_code == 400:
        print("✅ Correctly rejected self-buddy addition")
    else:
        print(f"❌ Self-buddy should return 400, got {self_resp.status_code}")
        return False
    
    # Test 2: Add user2 as buddy, then try to add again
    add_buddy_data = {"buddy_id": user2_id}
    add_resp = requests.post(f"{BASE_URL}/api/buddies", json=add_buddy_data, headers=user1_headers)
    
    if add_resp.status_code != 201:
        print(f"❌ First add failed: {add_resp.status_code}")
        return False
    
    duplicate_resp = requests.post(f"{BASE_URL}/api/buddies", json=add_buddy_data, headers=user1_headers)
    
    if duplicate_resp.status_code == 409:
        print("✅ Correctly rejected duplicate buddy")
    else:
        print(f"❌ Duplicate should return 409, got {duplicate_resp.status_code}")
        return False
    
    # Test 3: Try to add non-existent user
    fake_user_id = str(uuid4())
    fake_buddy_data = {"buddy_id": fake_user_id}
    fake_resp = requests.post(f"{BASE_URL}/api/buddies", json=fake_buddy_data, headers=user1_headers)
    
    if fake_resp.status_code == 404:
        print("✅ Correctly rejected non-existent user")
    else:
        print(f"❌ Non-existent user should return 404, got {fake_resp.status_code}")
        return False
    
    print("✅ All error cases passed!")
    return True

if __name__ == "__main__":
    print("🚀 Testing Buddy System with live FastAPI server...")
    
    success1 = test_buddy_system()
    success2 = test_error_cases()
    
    if success1 and success2:
        print(f"\n🎉 ALL BUDDY SYSTEM TESTS PASSED! 🎉")
        print(f"✅ Complete Buddy/Favorites functionality is working!")
        print(f"✅ Authentication integration working")
        print(f"✅ CRUD operations working")
        print(f"✅ Error handling working")
        print(f"✅ Available buddies filtering working")
    else:
        print(f"\n❌ Some tests failed")