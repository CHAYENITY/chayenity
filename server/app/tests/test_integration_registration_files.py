"""
Comprehensive integration test for two-step registration and file serving
This test validates the complete user journey and core API functionality
"""
import pytest
from fastapi.testclient import TestClient
import io
import tempfile
import os
import uuid
from PIL import Image

# Import your app
from app.main import app


class TestRegistrationAndFileFlow:
    """Test the complete registration and file upload flow"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.client = TestClient(app)
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "securepassword123"
    
    def create_test_image(self):
        """Create a test image for upload"""
        image = Image.new("RGB", (100, 100), color="red")
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="JPEG")
        img_buffer.seek(0)
        return img_buffer.read()
    
    def test_complete_user_journey(self):
        """Test complete user journey: register → login → profile setup → file upload"""
        
        # Step 1: Register user with basic information
        registration_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        reg_response = self.client.post("/api/auth/register", json=registration_data)
        assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"
        
        user_data = reg_response.json()
        assert user_data["email"] == self.test_email
        assert user_data["is_profile_complete"] is False
        assert user_data["first_name"] is None
        assert user_data["last_name"] is None
        
        print(f"✅ Step 1: User registration successful - {self.test_email}")
        
        # Step 2: Login to get access token
        login_data = {
            "username": self.test_email,
            "password": self.test_password
        }
        
        login_response = self.client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        tokens = login_response.json()
        assert "access_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("✅ Step 2: User login successful")
        
        # Step 3: Upload profile image before completing profile
        image_content = self.create_test_image()
        files = {"file": ("profile.jpg", io.BytesIO(image_content), "image/jpeg")}
        
        upload_response = self.client.put("/api/files/profile-image", files=files, headers=headers)
        assert upload_response.status_code == 200, f"Profile image upload failed: {upload_response.text}"
        
        upload_data = upload_response.json()
        assert "profile_image_url" in upload_data
        assert upload_data["message"] == "Profile image updated successfully"
        
        profile_image_url = upload_data["profile_image_url"]
        
        print("✅ Step 3: Profile image upload successful")
        
        # Step 4: Complete profile setup
        profile_data = {
            "first_name": "Test",
            "last_name": "User",
            "bio": "This is a test user for integration testing",
            "phone_number": "0812345678",
            "additional_contact": "Line: testuser",
            "current_position": "Software Tester",
            "address": {
                "address_line": "123 Test Street",
                "district": "Test District",
                "province": "Bangkok",
                "postal_code": "10110", 
                "country": "Thailand",
                "latitude": 13.7563,
                "longitude": 100.5018
            }
        }
        
        profile_response = self.client.put("/api/auth/profile-setup", json=profile_data, headers=headers)
        assert profile_response.status_code == 200, f"Profile setup failed: {profile_response.text}"
        
        profile_result = profile_response.json()
        assert profile_result["is_profile_complete"] is True
        assert profile_result["first_name"] == "Test"
        assert profile_result["last_name"] == "User"
        assert profile_result["profile_image_url"] == profile_image_url
        
        print("✅ Step 4: Profile setup successful")
        
        # Step 5: Test file serving
        serve_path = profile_image_url.replace("/api", "")
        serve_response = self.client.get(serve_path)
        assert serve_response.status_code == 200, f"File serving failed: {serve_response.text}"
        assert serve_response.headers["content-type"].startswith("image/")
        assert len(serve_response.content) > 0
        
        print("✅ Step 5: File serving successful")
        
        # Step 6: Test gig image upload
        gig_image = self.create_test_image()
        gig_files = {"file": ("gig.png", io.BytesIO(gig_image), "image/png")}
        
        gig_response = self.client.post("/api/files/upload/gig", files=gig_files, headers=headers)
        assert gig_response.status_code == 200, f"Gig upload failed: {gig_response.text}"
        
        gig_data = gig_response.json()
        assert gig_data["category"] == "gig"
        assert gig_data["original_filename"] == "gig.png"
        
        print("✅ Step 6: Gig image upload successful")
        
        print("🎉 Complete user journey test PASSED!")
        
        return {
            "user_email": self.test_email,
            "access_token": access_token,
            "profile_image_url": profile_image_url,
            "user_id": user_data["id"]
        }
    
    def test_duplicate_registration_prevention(self):
        """Test that duplicate email registration is properly prevented"""
        
        # First registration
        registration_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response1 = self.client.post("/api/auth/register", json=registration_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = self.client.post("/api/auth/register", json=registration_data)
        assert response2.status_code == 409
        assert "already registered" in response2.json()["detail"]
        
        print("✅ Duplicate email prevention working correctly")
    
    def test_file_upload_validation(self):
        """Test file upload validation and error handling"""
        
        # Create authenticated user
        test_data = self.test_complete_user_journey()
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        
        # Test invalid file type
        text_content = b"This is not an image"
        files = {"file": ("document.txt", io.BytesIO(text_content), "text/plain")}
        
        response = self.client.post("/api/files/upload/profile", files=files, headers=headers)
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]
        
        print("✅ File type validation working correctly")
        
        # Test unauthorized upload
        image_content = self.create_test_image()
        files = {"file": ("test.jpg", io.BytesIO(image_content), "image/jpeg")}
        
        response = self.client.post("/api/files/upload/profile", files=files)  # No auth
        assert response.status_code == 401
        
        print("✅ Authentication requirement working correctly")
    
    def test_file_listing_and_management(self):
        """Test file listing and management functionality"""
        
        # Create authenticated user and upload files
        test_data = self.test_complete_user_journey()
        headers = {"Authorization": f"Bearer {test_data['access_token']}"}
        
        # List profile files
        list_response = self.client.get("/api/files/list/profile", headers=headers)
        assert list_response.status_code == 200
        
        files_list = list_response.json()
        assert len(files_list) >= 1  # Should have at least the profile image
        
        for file_info in files_list:
            assert "file_id" in file_info
            assert "filename" in file_info
            assert "file_url" in file_info
            assert "uploaded_at" in file_info
        
        print(f"✅ File listing successful - Found {len(files_list)} files")


def test_api_health():
    """Simple test to verify API is responding"""
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ API health check passed")


def test_environment_setup():
    """Test that environment variables are properly configured"""
    import os
    
    required_vars = [
        'POSTGRES_SERVER', 'POSTGRES_PORT', 'POSTGRES_DB', 
        'POSTGRES_USER', 'POSTGRES_PASSWORD'
    ]
    
    for var in required_vars:
        assert os.getenv(var) is not None, f"Environment variable {var} is not set"
    
    print("✅ Environment configuration validated")


if __name__ == "__main__":
    """Run tests manually for debugging"""
    import os
    from dotenv import load_dotenv
    
    # Load environment
    load_dotenv()
    
    # Set required environment variables
    os.environ.setdefault('POSTGRES_SERVER', 'localhost')
    os.environ.setdefault('POSTGRES_PORT', '5432')
    os.environ.setdefault('POSTGRES_DB', 'hourz')
    os.environ.setdefault('POSTGRES_USER', 'admin')
    os.environ.setdefault('POSTGRES_PASSWORD', 'secret')
    os.environ.setdefault('ENVIRONMENT', 'local')
    
    print("🚀 Running Integration Tests")
    print("=" * 50)
    
    try:
        # Run health checks
        test_api_health()
        test_environment_setup()
        
        # Run main test suite
        test_instance = TestRegistrationAndFileFlow()
        test_instance.setup_method()
        
        # Test complete flow
        test_instance.test_complete_user_journey()
        
        # Test edge cases
        test_instance2 = TestRegistrationAndFileFlow()
        test_instance2.setup_method()
        test_instance2.test_duplicate_registration_prevention()
        
        print("\n" + "=" * 50)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Two-step registration flow working")
        print("✅ File upload and serving working")
        print("✅ Authentication and validation working")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()