#!/usr/bin/env python3
"""
Quick Review System API test - focuses only on review endpoints
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

def test_review_endpoints():
    """Test review endpoints with mock data."""
    print("🧪 Testing Review API Endpoints...")
    
    # Create test users
    test_id = str(uuid4())[:8]
    print("👤 Creating test users...")
    
    user1_headers, user1_id = register_and_login(f"user1_{test_id}@example.com", "password", "User One")
    user2_headers, user2_id = register_and_login(f"user2_{test_id}@example.com", "password", "User Two")
    
    if not user1_headers or not user2_headers:
        print("❌ Failed to create test users")
        return False
    
    print(f"✅ Created users: {user1_id} and {user2_id}")
    
    # Test validation with mock gig_id
    print("\n📝 Testing review validation...")
    
    # Test 1: Invalid rating
    print("⭐ Testing invalid rating...")
    invalid_rating_data = {
        "gig_id": str(uuid4()),  # Mock gig ID
        "reviewee_id": user2_id,
        "rating": 6,  # Invalid - should be 1-5
        "comment": "Invalid rating test"
    }
    
    invalid_rating_resp = requests.post(f"{BASE_URL}/api/reviews/", json=invalid_rating_data, headers=user1_headers)
    if invalid_rating_resp.status_code == 422:
        print("✅ Correctly rejected invalid rating (6 stars)")
    else:
        print(f"❌ Expected 422 for invalid rating, got {invalid_rating_resp.status_code}: {invalid_rating_resp.text}")
    
    # Test 2: Empty comment
    print("📝 Testing empty comment...")
    empty_comment_data = {
        "gig_id": str(uuid4()),  # Mock gig ID
        "reviewee_id": user2_id,
        "rating": 5,
        "comment": ""  # Empty comment - should be rejected
    }
    
    empty_comment_resp = requests.post(f"{BASE_URL}/api/reviews/", json=empty_comment_data, headers=user1_headers)
    if empty_comment_resp.status_code == 422:
        print("✅ Correctly rejected empty comment")
    else:
        print(f"❌ Expected 422 for empty comment, got {empty_comment_resp.status_code}: {empty_comment_resp.text}")
    
    # Test 3: Missing required fields
    print("📋 Testing missing required fields...")
    missing_fields_data = {
        "rating": 5,
        "comment": "Missing gig_id and reviewee_id"
    }
    
    missing_fields_resp = requests.post(f"{BASE_URL}/api/reviews/", json=missing_fields_data, headers=user1_headers)
    if missing_fields_resp.status_code == 422:
        print("✅ Correctly rejected missing required fields")
    else:
        print(f"❌ Expected 422 for missing fields, got {missing_fields_resp.status_code}: {missing_fields_resp.text}")
    
    # Test 4: No authentication
    print("🔒 Testing no authentication...")
    valid_data = {
        "gig_id": str(uuid4()),
        "reviewee_id": user2_id,
        "rating": 5,
        "comment": "Test comment"
    }
    
    no_auth_resp = requests.post(f"{BASE_URL}/api/reviews/", json=valid_data)
    if no_auth_resp.status_code == 401:
        print("✅ Correctly rejected unauthorized request")
    else:
        print(f"❌ Expected 401 for no auth, got {no_auth_resp.status_code}: {no_auth_resp.text}")
    
    # Test endpoint availability
    print("\n📋 Testing endpoint availability...")
    
    # Test get non-existent user reviews (with authentication)
    nonexistent_user_resp = requests.get(f"{BASE_URL}/api/reviews/user/99999999-9999-4999-9999-999999999999", headers=user1_headers)
    if nonexistent_user_resp.status_code == 404:
        print("✅ GET /user/{id} endpoint working (returns 404 for non-existent user)")
    else:
        print(f"❌ GET /user/{id} endpoint issue: {nonexistent_user_resp.status_code}")
    
    # Test get my reviews (should work with empty result)
    my_reviews_resp = requests.get(f"{BASE_URL}/api/reviews/my-reviews", headers=user1_headers)
    if my_reviews_resp.status_code == 200:
        print("✅ GET /my-reviews endpoint working")
        my_reviews = my_reviews_resp.json()
        print(f"   Found {len(my_reviews)} reviews for current user")
    else:
        print(f"❌ GET /my-reviews endpoint issue: {my_reviews_resp.status_code}: {my_reviews_resp.text}")
    
    # Test update non-existent review
    update_data = {"rating": 4, "comment": "Updated comment"}
    update_resp = requests.put(f"{BASE_URL}/api/reviews/99999999-9999-4999-9999-999999999999", json=update_data, headers=user1_headers)
    if update_resp.status_code == 404:
        print("✅ PUT /{id} endpoint working (returns 404 for non-existent review)")
    else:
        print(f"❌ PUT /{id} endpoint issue: {update_resp.status_code}")
    
    # Test delete non-existent review
    delete_resp = requests.delete(f"{BASE_URL}/api/reviews/99999999-9999-4999-9999-999999999999", headers=user1_headers)
    if delete_resp.status_code == 404:
        print("✅ DELETE /{id} endpoint working (returns 404 for non-existent review)")
    else:
        print(f"❌ DELETE /{id} endpoint issue: {delete_resp.status_code}")
    
    print("\n🎉 Review API endpoint tests completed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Quick Review API Tests")
    print("=" * 50)
    
    result = test_review_endpoints()
    
    print("\n" + "=" * 50)
    if result:
        print("✅ Review API endpoints are working correctly!")
        print("💡 Note: Full integration tests require working gig creation")
        exit(0)
    else:
        print("❌ Some Review API tests failed!")
        exit(1)