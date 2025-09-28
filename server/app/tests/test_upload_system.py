"""
Test cases for the file upload system.
Tests profile image upload, gig image upload, and file serving.
Uses live server approach like existing working tests.
"""

import io
import requests
from uuid import uuid4

from PIL import Image


# Test settings
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
    return {"Authorization": f"Bearer {token}"}, user_info


def test_upload_profile_image_success():
    """Test successful profile image upload."""
    print("\n=== Testing Profile Image Upload ===")
    
    # Create test user
    email = f"upload_test_{uuid4().hex[:8]}@example.com"
    headers, user_info = register_and_login(email, "testpass123")
    if not headers:
        assert False, "Failed to create test user"
    
    # Create a test image in memory
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Upload the image
    files = {"file": ("test_profile.png", img_buffer, "image/png")}
    response = requests.post(f"{BASE_URL}/api/upload/profile", headers=headers, files=files)
    
    print(f"Upload response: {response.status_code}")
    if response.status_code != 201:
        print(f"Upload failed: {response.text}")
        assert False, "Profile image upload failed"
    
    data = response.json()
    print(f"Upload successful: {data['filename']}")
    
    # Verify response structure
    assert "file_id" in data
    assert data["filename"] != data["original_filename"]  # UUID filename
    assert data["original_filename"] == "test_profile.png"
    assert data["content_type"] == "image/png"
    assert data["file_size"] > 0
    assert data["url"].startswith("http://")
    assert "uploaded_at" in data
    
    return data["file_id"]


def test_upload_gig_image_success():
    """Test successful gig image upload."""
    print("\n=== Testing Gig Image Upload ===")
    
    # Create test user
    email = f"gig_upload_{uuid4().hex[:8]}@example.com"
    headers, user_info = register_and_login(email, "testpass123")
    if not headers:
        assert False, "Failed to create test user"
    
    # Create a test image
    img = Image.new('RGB', (200, 200), color='blue')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    files = {"file": ("gig_image.jpg", img_buffer, "image/jpeg")}
    response = requests.post(f"{BASE_URL}/api/upload/gig", headers=headers, files=files)
    
    print(f"Gig upload response: {response.status_code}")
    if response.status_code != 201:
        print(f"Gig upload failed: {response.text}")
        assert False, "Gig image upload failed"
    
    data = response.json()
    print(f"Gig upload successful: {data['filename']}")
    
    assert data["content_type"] == "image/jpeg"
    assert data["original_filename"] == "gig_image.jpg"
    
    return data["file_id"]


def test_upload_invalid_file_type():
    """Test uploading invalid file type."""
    print("\n=== Testing Invalid File Type ===")
    
    # Create test user
    email = f"invalid_test_{uuid4().hex[:8]}@example.com"
    headers, user_info = register_and_login(email, "testpass123")
    if not headers:
        assert False, "Failed to create test user"
    
    # Create a text file
    text_content = b"This is not an image"
    files = {"file": ("document.txt", text_content, "text/plain")}
    
    response = requests.post(f"{BASE_URL}/api/upload/profile", headers=headers, files=files)
    
    print(f"Invalid file response: {response.status_code}")
    assert response.status_code == 415  # FastAPI returns 415 for unsupported media types
    assert "Unsupported file type" in response.json()["detail"]
    print("✓ Invalid file type correctly rejected")


def test_serve_uploaded_file():
    """Test serving an uploaded file."""
    print("\n=== Testing File Serving ===")
    
    # First upload a file
    file_id = test_upload_profile_image_success()
    
    # Then serve it
    response = requests.get(f"{BASE_URL}/api/upload/{file_id}")
    
    print(f"File serve response: {response.status_code}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0
    print("✓ File served successfully")


def test_serve_nonexistent_file():
    """Test serving a file that doesn't exist."""
    print("\n=== Testing Nonexistent File ===")
    
    fake_uuid = "12345678-1234-1234-1234-123456789012"
    response = requests.get(f"{BASE_URL}/api/upload/{fake_uuid}")
    
    print(f"Nonexistent file response: {response.status_code}")
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]
    print("✓ Nonexistent file correctly returns 404")


def test_get_my_uploaded_files():
    """Test getting user's uploaded files."""
    print("\n=== Testing My Files List ===")
    
    # Create test user
    email = f"my_files_{uuid4().hex[:8]}@example.com"
    headers, user_info = register_and_login(email, "testpass123")
    if not headers:
        assert False, "Failed to create test user"
    
    # Upload a couple of files
    img1 = Image.new('RGB', (50, 50), color='red')
    img1_buffer = io.BytesIO()
    img1.save(img1_buffer, format='PNG')
    img1_buffer.seek(0)
    
    img2 = Image.new('RGB', (60, 60), color='green')
    img2_buffer = io.BytesIO()
    img2.save(img2_buffer, format='JPEG')
    img2_buffer.seek(0)
    
    # Upload profile image
    files1 = {"file": ("profile.png", img1_buffer, "image/png")}
    response1 = requests.post(f"{BASE_URL}/api/upload/profile", headers=headers, files=files1)
    assert response1.status_code == 201
    profile_file_id = response1.json()["file_id"]
    
    # Upload gig image
    files2 = {"file": ("gig.jpg", img2_buffer, "image/jpeg")}
    response2 = requests.post(f"{BASE_URL}/api/upload/gig", headers=headers, files=files2)
    assert response2.status_code == 201
    gig_file_id = response2.json()["file_id"]
    
    # Get all files
    response = requests.get(f"{BASE_URL}/api/upload/my-files/", headers=headers)
    
    print(f"My files response: {response.status_code}")
    assert response.status_code == 200
    files = response.json()
    
    assert len(files) >= 2
    file_ids = [f["file_id"] for f in files]
    assert profile_file_id in file_ids
    assert gig_file_id in file_ids
    print(f"✓ Found {len(files)} files for user")


def test_delete_uploaded_file():
    """Test deleting an uploaded file."""
    print("\n=== Testing File Deletion ===")
    
    # Create test user
    email = f"delete_test_{uuid4().hex[:8]}@example.com"
    headers, user_info = register_and_login(email, "testpass123")
    if not headers:
        assert False, "Failed to create test user"
    
    # Upload a file
    img = Image.new('RGB', (30, 30), color='yellow')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    files = {"file": ("delete_me.png", img_buffer, "image/png")}
    response = requests.post(f"{BASE_URL}/api/upload/profile", headers=headers, files=files)
    assert response.status_code == 201
    file_id = response.json()["file_id"]
    
    # Delete it
    response = requests.delete(f"{BASE_URL}/api/upload/{file_id}", headers=headers)
    print(f"Delete response: {response.status_code}")
    assert response.status_code == 204
    
    # Try to serve it (should fail)
    response = requests.get(f"{BASE_URL}/api/upload/{file_id}")
    assert response.status_code == 404
    print("✓ File deleted successfully")


def test_set_profile_image():
    """Test setting profile image URL."""
    print("\n=== Testing Set Profile Image ===")
    
    # Create test user
    email = f"set_profile_{uuid4().hex[:8]}@example.com"
    headers, user_info = register_and_login(email, "testpass123")
    if not headers:
        assert False, "Failed to create test user"
    
    # Upload an image first
    img = Image.new('RGB', (40, 40), color='purple')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    files = {"file": ("profile_set.png", img_buffer, "image/png")}
    upload_response = requests.post(f"{BASE_URL}/api/upload/profile", headers=headers, files=files)
    assert upload_response.status_code == 201
    file_id = upload_response.json()["file_id"]
    
    image_url = f"http://localhost:8000/api/upload/{file_id}"
    
    # Set as profile image
    response = requests.put(
        f"{BASE_URL}/api/upload/profile/set",
        headers=headers,
        json={"profile_image_url": image_url}
    )
    
    print(f"Set profile image response: {response.status_code}")
    assert response.status_code == 200
    assert "Profile image updated successfully" in response.json()["message"]
    print("✓ Profile image URL set successfully")


def test_upload_without_auth():
    """Test uploading without authentication."""
    print("\n=== Testing Upload Without Auth ===")
    
    img = Image.new('RGB', (50, 50), color='green')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    files = {"file": ("test.png", img_buffer, "image/png")}
    response = requests.post(f"{BASE_URL}/api/upload/profile", files=files)
    
    print(f"No auth response: {response.status_code}")
    assert response.status_code == 401
    print("✓ Upload without auth correctly rejected")


def run_all_tests():
    """Run all upload system tests."""
    print("\n🚀 STARTING UPLOAD SYSTEM TESTS")
    print("=" * 50)
    
    try:
        test_upload_profile_image_success()
        test_upload_gig_image_success()
        test_upload_invalid_file_type()
        test_serve_uploaded_file()
        test_serve_nonexistent_file()
        test_get_my_uploaded_files()
        test_delete_uploaded_file()
        test_set_profile_image()
        test_upload_without_auth()
        
        print("\n" + "=" * 50)
        print("🎉 ALL UPLOAD SYSTEM TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()