"""
Test the Buddy System API endpoints.

Tests:
1. Add buddy
2. List buddies
3. Get buddy details
4. Update buddy notes
5. Remove buddy
6. Get available buddies
7. Error cases (duplicate, self-add, not found)
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app


def register_and_login(client: TestClient, email: str, password: str, full_name: str = "Test User"):
    """Register a user and return their auth token."""
    # Register
    register_data = {"email": email, "password": password, "full_name": full_name}
    register_resp = client.post("/api/auth/register", json=register_data)
    if register_resp.status_code not in (200, 201, 409):  # 409 = already exists
        pytest.fail(f"Registration failed: {register_resp.text}")
    
    # Login
    login_data = {"username": email, "password": password}
    login_resp = client.post("/api/auth/login", data=login_data)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_buddy_system_flow():
    """Test complete buddy system workflow."""
    with TestClient(app) as client:
        # Create 3 test users
        user1_headers = register_and_login(client, "user1@buddy.test", "password", "User One")
        user2_headers = register_and_login(client, "user2@buddy.test", "password", "User Two")
        user3_headers = register_and_login(client, "user3@buddy.test", "password", "User Three")
        
        # Get user2 and user3 IDs for adding as buddies
        user2_profile = client.get("/api/users/me", headers=user2_headers)
        user3_profile = client.get("/api/users/me", headers=user3_headers)
        assert user2_profile.status_code == 200
        assert user3_profile.status_code == 200
        
        user2_id = user2_profile.json()["id"]
        user3_id = user3_profile.json()["id"]
        
        # Test 1: User1 adds User2 as buddy
        add_buddy_data = {"buddy_id": user2_id, "notes": "Great helper!"}
        add_resp = client.post("/api/buddies", json=add_buddy_data, headers=user1_headers)
        assert add_resp.status_code == 201, f"Add buddy failed: {add_resp.text}"
        
        buddy_response = add_resp.json()
        assert buddy_response["buddy_id"] == user2_id
        assert buddy_response["notes"] == "Great helper!"
        assert buddy_response["buddy_full_name"] == "User Two"
        
        # Test 2: User1 adds User3 as buddy (no notes)
        add_buddy_data2 = {"buddy_id": user3_id}
        add_resp2 = client.post("/api/buddies", json=add_buddy_data2, headers=user1_headers)
        assert add_resp2.status_code == 201
        
        # Test 3: Get buddy list (should have 2 buddies)
        buddies_resp = client.get("/api/buddies", headers=user1_headers)
        assert buddies_resp.status_code == 200
        
        buddy_list = buddies_resp.json()
        assert len(buddy_list["buddies"]) == 2
        assert buddy_list["total"] == 2
        
        # Verify buddy details are included
        buddy_names = [b["buddy_full_name"] for b in buddy_list["buddies"]]
        assert "User Two" in buddy_names
        assert "User Three" in buddy_names
        
        # Test 4: Get specific buddy details
        buddy_details_resp = client.get(f"/api/buddies/{user2_id}", headers=user1_headers)
        assert buddy_details_resp.status_code == 200
        
        buddy_details = buddy_details_resp.json()
        assert buddy_details["buddy_id"] == user2_id
        assert buddy_details["notes"] == "Great helper!"
        assert buddy_details["buddy_full_name"] == "User Two"
        
        # Test 5: Update buddy notes
        update_data = {"notes": "Updated: Excellent communication!"}
        update_resp = client.put(f"/api/buddies/{user2_id}", json=update_data, headers=user1_headers)
        assert update_resp.status_code == 200
        
        updated_buddy = update_resp.json()
        assert updated_buddy["notes"] == "Updated: Excellent communication!"
        
        # Test 6: Set User3 as available and check available buddies
        availability_data = {"is_available": True}
        user3_availability = client.put("/api/users/availability", json=availability_data, headers=user3_headers)
        assert user3_availability.status_code == 200
        
        available_resp = client.get("/api/buddies/available", headers=user1_headers)
        assert available_resp.status_code == 200
        
        available_buddies = available_resp.json()
        # Should have at least User3 (and possibly User2 if they were already available)
        available_names = [b["buddy_full_name"] for b in available_buddies["buddies"]]
        assert "User Three" in available_names
        
        # Test 7: Remove buddy
        remove_resp = client.delete(f"/api/buddies/{user2_id}", headers=user1_headers)
        assert remove_resp.status_code == 204
        
        # Verify buddy was removed
        buddies_after_removal = client.get("/api/buddies", headers=user1_headers)
        assert buddies_after_removal.status_code == 200
        remaining_buddies = buddies_after_removal.json()
        assert len(remaining_buddies["buddies"]) == 1
        remaining_names = [b["buddy_full_name"] for b in remaining_buddies["buddies"]]
        assert "User Two" not in remaining_names
        assert "User Three" in remaining_names


def test_buddy_system_error_cases():
    """Test error cases for buddy system."""
    with TestClient(app) as client:
        # Create 2 test users
        user1_headers = register_and_login(client, "error1@buddy.test", "password", "Error User 1")
        user2_headers = register_and_login(client, "error2@buddy.test", "password", "Error User 2")
        
        # Get user IDs
        user1_profile = client.get("/api/users/me", headers=user1_headers)
        user2_profile = client.get("/api/users/me", headers=user2_headers)
        user1_id = user1_profile.json()["id"]
        user2_id = user2_profile.json()["id"]
        
        # Test 1: Try to add self as buddy
        self_buddy_data = {"buddy_id": user1_id}
        self_resp = client.post("/api/buddies", json=self_buddy_data, headers=user1_headers)
        assert self_resp.status_code == 400
        assert "Cannot add yourself" in self_resp.json()["detail"]
        
        # Test 2: Add User2 as buddy first
        add_buddy_data = {"buddy_id": user2_id}
        add_resp = client.post("/api/buddies", json=add_buddy_data, headers=user1_headers)
        assert add_resp.status_code == 201
        
        # Test 3: Try to add same buddy again (duplicate)
        duplicate_resp = client.post("/api/buddies", json=add_buddy_data, headers=user1_headers)
        assert duplicate_resp.status_code == 409
        assert "already in your buddy list" in duplicate_resp.json()["detail"]
        
        # Test 4: Try to add non-existent user
        fake_user_id = str(uuid4())
        fake_buddy_data = {"buddy_id": fake_user_id}
        fake_resp = client.post("/api/buddies", json=fake_buddy_data, headers=user1_headers)
        assert fake_resp.status_code == 404
        assert "User not found" in fake_resp.json()["detail"]
        
        # Test 5: Try to get details of non-buddy
        fake_user_id2 = str(uuid4())
        details_resp = client.get(f"/api/buddies/{fake_user_id2}", headers=user1_headers)
        assert details_resp.status_code == 404
        assert "Buddy not found" in details_resp.json()["detail"]
        
        # Test 6: Try to remove non-existent buddy
        remove_resp = client.delete(f"/api/buddies/{fake_user_id2}", headers=user1_headers)
        assert remove_resp.status_code == 404
        assert "Buddy not found" in remove_resp.json()["detail"]


if __name__ == "__main__":
    print("Running Buddy System tests manually...")
    test_buddy_system_flow()
    test_buddy_system_error_cases()
    print("All Buddy System tests passed! 🎉")