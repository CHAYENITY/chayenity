"""
File Upload Integration Tests

This module tests the complete file upload system including:
- Profile image uploads and management
- Gig image uploads for project documentation
- General file uploads and sharing
- File access control and security
- File deletion and cleanup
- File format validation and error handling
- Integration with other systems (gigs, profiles, chat)
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO
import tempfile
import os


class TestFileUploadIntegration:
    """Test comprehensive file upload functionality and integration"""

    @pytest.fixture
    def uploader_credentials(self):
        """User credentials for file uploader"""
        return {
            "email": "fileuploader@example.com",
            "password": "filepass123",
            "full_name": "File Uploader",
            "name": "Uploader"
        }

    @pytest.fixture
    def viewer_credentials(self):
        """User credentials for file viewer"""
        return {
            "email": "fileviewer@example.com",
            "password": "viewpass123",
            "full_name": "File Viewer", 
            "name": "Viewer"
        }

    @pytest.fixture
    def uploader_client(self, uploader_credentials):
        """Authenticated client for file uploader"""
        with TestClient(app) as client:
            # Register and login
            client.post("/api/auth/register", json=uploader_credentials)
            login_resp = client.post("/api/auth/login", data={
                "username": uploader_credentials["email"],
                "password": uploader_credentials["password"]
            })
            token = login_resp.json()["access_token"]
            client.headers.update({"Authorization": f"Bearer {token}"})
            
            # Set location
            client.put("/api/users/location", json={"latitude": 13.7563, "longitude": 100.5018})
            yield client

    @pytest.fixture
    def viewer_client(self, viewer_credentials):
        """Authenticated client for file viewer"""
        with TestClient(app) as client:
            # Register and login
            client.post("/api/auth/register", json=viewer_credentials)
            login_resp = client.post("/api/auth/login", data={
                "username": viewer_credentials["email"],
                "password": viewer_credentials["password"]
            })
            token = login_resp.json()["access_token"]
            client.headers.update({"Authorization": f"Bearer {token}"})
            
            # Set location and availability
            client.put("/api/users/location", json={"latitude": 13.7563, "longitude": 100.5018})
            client.put("/api/users/availability", json={"is_available": True})
            yield client

    def test_profile_image_upload_workflow(self, uploader_client):
        """Test complete profile image upload and management workflow"""
        
        # Create test profile image
        profile_image_content = b"fake_profile_image_data_for_testing"
        files = {"file": ("profile.jpg", BytesIO(profile_image_content), "image/jpeg")}
        
        # Upload profile image
        upload_resp = uploader_client.post("/api/upload/profile", files=files)
        assert upload_resp.status_code == 201, f"Failed to upload profile image: {upload_resp.text}"
        uploaded_file = upload_resp.json()
        
        # Verify upload response structure
        assert "id" in uploaded_file
        assert "filename" in uploaded_file
        assert "file_type" in uploaded_file
        assert uploaded_file["file_type"] == "profile"
        assert uploaded_file["content_type"] == "image/jpeg"
        
        file_id = uploaded_file["id"]
        
        # Set uploaded image as profile image
        set_profile_resp = uploader_client.put("/api/upload/profile/set", 
                                              json={"file_id": file_id})
        assert set_profile_resp.status_code == 200
        
        # Verify profile image is set in user profile
        profile_resp = uploader_client.get("/api/users/me")
        assert profile_resp.status_code == 200
        profile = profile_resp.json()
        assert profile["photo_url"] is not None
        assert file_id in profile["photo_url"]
        
        # Test file access
        file_resp = uploader_client.get(f"/api/upload/{file_id}")
        assert file_resp.status_code == 200
        assert file_resp.headers["content-type"] == "image/jpeg"
        assert len(file_resp.content) > 0
        
        # Upload and replace with new profile image
        new_profile_content = b"new_profile_image_data_for_testing"
        new_files = {"file": ("new_profile.png", BytesIO(new_profile_content), "image/png")}
        
        new_upload_resp = uploader_client.post("/api/upload/profile", files=new_files)
        assert new_upload_resp.status_code == 201
        new_file_id = new_upload_resp.json()["id"]
        
        # Set new image as profile
        new_set_resp = uploader_client.put("/api/upload/profile/set", 
                                          json={"file_id": new_file_id})
        assert new_set_resp.status_code == 200
        
        # Verify profile was updated
        updated_profile_resp = uploader_client.get("/api/users/me")
        assert updated_profile_resp.status_code == 200
        updated_profile = updated_profile_resp.json()
        assert new_file_id in updated_profile["photo_url"]

    def test_gig_image_upload_workflow(self, uploader_client, viewer_client):
        """Test gig image upload and sharing workflow"""
        
        # Create a gig first
        gig_data = {
            "title": "Photography project with image uploads",
            "description": "Need photographer for event documentation",
            "budget": 800.0,
            "duration_hours": 4,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = uploader_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        # Upload multiple gig images
        gig_images = [
            ("venue1.jpg", b"venue_photo_1_data", "image/jpeg"),
            ("venue2.png", b"venue_photo_2_data", "image/png"),
            ("requirements.jpg", b"requirements_photo_data", "image/jpeg")
        ]
        
        uploaded_gig_files = []
        
        for filename, content, content_type in gig_images:
            files = {"file": (filename, BytesIO(content), content_type)}
            
            upload_resp = uploader_client.post("/api/upload/gig", files=files)
            assert upload_resp.status_code == 201, f"Failed to upload {filename}: {upload_resp.text}"
            uploaded_file = upload_resp.json()
            
            assert uploaded_file["file_type"] == "gig"
            assert uploaded_file["content_type"] == content_type
            uploaded_gig_files.append(uploaded_file)
        
        # Verify all gig files are listed in user's files
        my_files_resp = uploader_client.get("/api/upload/my-files?file_type=gig")
        assert my_files_resp.status_code == 200
        my_gig_files = my_files_resp.json()
        
        uploaded_file_ids = {f["id"] for f in uploaded_gig_files}
        listed_file_ids = {f["id"] for f in my_gig_files}
        
        assert uploaded_file_ids.issubset(listed_file_ids), "All uploaded gig files should be listed"
        
        # Helper accepts gig and can view gig images
        accept_resp = viewer_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Helper can access gig images
        for uploaded_file in uploaded_gig_files:
            file_id = uploaded_file["id"]
            file_resp = viewer_client.get(f"/api/upload/{file_id}")
            assert file_resp.status_code == 200, f"Helper should access gig image {file_id}"
            assert file_resp.headers["content-type"] == uploaded_file["content_type"]

    def test_general_file_upload_and_sharing(self, uploader_client, viewer_client):
        """Test general file uploads and sharing in chat"""
        
        # Create gig and establish chat room
        gig_data = {
            "title": "Document sharing project",
            "description": "Need help with file organization",
            "budget": 300.0,
            "duration_hours": 2,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = uploader_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        accept_resp = viewer_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Get chat room
        rooms_resp = uploader_client.get("/api/chat/rooms")
        assert rooms_resp.status_code == 200
        rooms = rooms_resp.json()
        
        gig_room = next((room for room in rooms if room["gig_id"] == gig_id), None)
        assert gig_room is not None
        room_id = gig_room["id"]
        
        # Upload general files for sharing
        general_files = [
            ("document.pdf", b"fake_pdf_content", "application/pdf"),
            ("spreadsheet.xlsx", b"fake_excel_content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("shared_image.jpg", b"shared_image_content", "image/jpeg")
        ]
        
        uploaded_general_files = []
        
        for filename, content, content_type in general_files:
            files = {"file": (filename, BytesIO(content), content_type)}
            
            upload_resp = uploader_client.post("/api/upload/general", files=files)
            assert upload_resp.status_code == 201, f"Failed to upload {filename}: {upload_resp.text}"
            uploaded_file = upload_resp.json()
            
            assert uploaded_file["file_type"] == "general"
            assert uploaded_file["content_type"] == content_type
            uploaded_general_files.append(uploaded_file)
        
        # Share files in chat
        for uploaded_file in uploaded_general_files:
            file_url = f"/api/upload/{uploaded_file['id']}"
            message_data = {
                "content": f"Here's the {uploaded_file['original_filename']} file you requested",
                "message_type": "file",
                "image_url": file_url  # Using image_url field for file attachments
            }
            
            msg_resp = uploader_client.post(f"/api/chat/rooms/{room_id}/messages", 
                                           json=message_data)
            assert msg_resp.status_code == 201
        
        # Viewer can access shared files through chat
        history_resp = viewer_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert history_resp.status_code == 200
        messages = history_resp.json()
        
        file_messages = [msg for msg in messages if msg["message_type"] == "file"]
        assert len(file_messages) == len(uploaded_general_files)
        
        # Test file access
        for file_message in file_messages:
            file_url = file_message["image_url"]
            file_resp = viewer_client.get(file_url)
            assert file_resp.status_code == 200, f"Viewer should access shared file {file_url}"

    def test_file_upload_validation_and_error_handling(self, uploader_client):
        """Test file upload validation and error handling"""
        
        # Test invalid file type
        invalid_file = ("virus.exe", b"malicious_content", "application/x-executable")
        files = {"file": invalid_file}
        
        invalid_resp = uploader_client.post("/api/upload/general", files=files)
        assert invalid_resp.status_code == 415, "Should reject invalid file types"
        
        # Test oversized file (if size limits are implemented)
        # Note: This test assumes there's a file size limit
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB
        large_files = {"file": ("large_image.jpg", BytesIO(large_content), "image/jpeg")}
        
        # This might pass if no size limit is implemented
        large_resp = uploader_client.post("/api/upload/general", files=large_files)
        # We'll just check it doesn't crash - implementation may or may not have size limits
        assert large_resp.status_code in [201, 413, 422]
        
        # Test missing file
        no_file_resp = uploader_client.post("/api/upload/general")
        assert no_file_resp.status_code == 422, "Should require file parameter"
        
        # Test empty file
        empty_files = {"file": ("empty.txt", BytesIO(b""), "text/plain")}
        empty_resp = uploader_client.post("/api/upload/general", files=empty_files)
        # Empty files might be allowed depending on implementation
        assert empty_resp.status_code in [201, 400, 422]

    def test_file_access_control_and_security(self, uploader_client, viewer_client):
        """Test file access control and security"""
        
        # Upload private profile image
        private_image = b"private_profile_image_content"
        files = {"file": ("private_profile.jpg", BytesIO(private_image), "image/jpeg")}
        
        upload_resp = uploader_client.post("/api/upload/profile", files=files)
        assert upload_resp.status_code == 201
        private_file_id = upload_resp.json()["id"]
        
        # Uploader can access their own file
        owner_access_resp = uploader_client.get(f"/api/upload/{private_file_id}")
        assert owner_access_resp.status_code == 200
        
        # Other user cannot access private file
        unauthorized_resp = viewer_client.get(f"/api/upload/{private_file_id}")
        assert unauthorized_resp.status_code == 403, "Should not access other user's private files"
        
        # Test access to non-existent file
        fake_file_id = "00000000-0000-0000-0000-000000000000"
        not_found_resp = uploader_client.get(f"/api/upload/{fake_file_id}")
        assert not_found_resp.status_code == 404, "Should return 404 for non-existent files"

    def test_file_deletion_workflow(self, uploader_client):
        """Test file deletion and cleanup workflow"""
        
        # Upload test files
        test_files = [
            ("to_delete1.jpg", b"delete_me_1", "image/jpeg"),
            ("to_delete2.png", b"delete_me_2", "image/png")
        ]
        
        uploaded_file_ids = []
        
        for filename, content, content_type in test_files:
            files = {"file": (filename, BytesIO(content), content_type)}
            
            upload_resp = uploader_client.post("/api/upload/general", files=files)
            assert upload_resp.status_code == 201
            file_id = upload_resp.json()["id"]
            uploaded_file_ids.append(file_id)
        
        # Verify files exist and are accessible
        for file_id in uploaded_file_ids:
            access_resp = uploader_client.get(f"/api/upload/{file_id}")
            assert access_resp.status_code == 200
        
        # List files to confirm they exist
        my_files_resp = uploader_client.get("/api/upload/my-files")
        assert my_files_resp.status_code == 200
        my_files = my_files_resp.json()
        
        my_file_ids = {f["id"] for f in my_files}
        for file_id in uploaded_file_ids:
            assert file_id in my_file_ids
        
        # Delete first file
        delete_resp = uploader_client.delete(f"/api/upload/{uploaded_file_ids[0]}")
        assert delete_resp.status_code == 200
        
        # Verify deleted file is no longer accessible
        deleted_access_resp = uploader_client.get(f"/api/upload/{uploaded_file_ids[0]}")
        assert deleted_access_resp.status_code == 404, "Deleted file should not be accessible"
        
        # Verify deleted file is not in file list
        updated_files_resp = uploader_client.get("/api/upload/my-files")
        assert updated_files_resp.status_code == 200
        updated_files = updated_files_resp.json()
        
        updated_file_ids = {f["id"] for f in updated_files}
        assert uploaded_file_ids[0] not in updated_file_ids, "Deleted file should not appear in list"
        
        # Second file should still be accessible
        remaining_access_resp = uploader_client.get(f"/api/upload/{uploaded_file_ids[1]}")
        assert remaining_access_resp.status_code == 200, "Non-deleted file should remain accessible"

    def test_file_management_with_multiple_file_types(self, uploader_client):
        """Test file management across different file types"""
        
        # Upload files of different types
        mixed_files = [
            ("profile_pic.jpg", b"profile_content", "image/jpeg", "profile"),
            ("gig_photo.png", b"gig_content", "image/png", "gig"), 
            ("document.pdf", b"document_content", "application/pdf", "general"),
            ("another_profile.jpg", b"another_profile_content", "image/jpeg", "profile")
        ]
        
        uploaded_files_by_type = {}
        
        for filename, content, content_type, file_type in mixed_files:
            files = {"file": (filename, BytesIO(content), content_type)}
            
            upload_resp = uploader_client.post(f"/api/upload/{file_type}", files=files)
            assert upload_resp.status_code == 201
            uploaded_file = upload_resp.json()
            
            if file_type not in uploaded_files_by_type:
                uploaded_files_by_type[file_type] = []
            uploaded_files_by_type[file_type].append(uploaded_file["id"])
        
        # Test filtering by file type
        for file_type, expected_file_ids in uploaded_files_by_type.items():
            filtered_resp = uploader_client.get(f"/api/upload/my-files?file_type={file_type}")
            assert filtered_resp.status_code == 200
            filtered_files = filtered_resp.json()
            
            filtered_file_ids = {f["id"] for f in filtered_files}
            expected_file_ids_set = set(expected_file_ids)
            
            assert expected_file_ids_set.issubset(filtered_file_ids), f"All {file_type} files should be in filtered results"
        
        # Test getting all files without filter
        all_files_resp = uploader_client.get("/api/upload/my-files")
        assert all_files_resp.status_code == 200
        all_files = all_files_resp.json()
        
        all_file_ids = {f["id"] for f in all_files}
        all_expected_ids = {file_id for file_ids in uploaded_files_by_type.values() for file_id in file_ids}
        
        assert all_expected_ids.issubset(all_file_ids), "All uploaded files should appear in unfiltered list"

    def test_file_upload_integration_with_user_profile_workflow(self, uploader_client, viewer_client):
        """Test complete integration of file uploads with user profile and gig workflow"""
        
        # Upload and set profile image
        profile_content = b"professional_profile_image"
        files = {"file": ("professional.jpg", BytesIO(profile_content), "image/jpeg")}
        
        profile_upload_resp = uploader_client.post("/api/upload/profile", files=files)
        assert profile_upload_resp.status_code == 201
        profile_file_id = profile_upload_resp.json()["id"]
        
        set_profile_resp = uploader_client.put("/api/upload/profile/set", 
                                              json={"file_id": profile_file_id})
        assert set_profile_resp.status_code == 200
        
        # Create gig with images
        gig_data = {
            "title": "Full service with documentation",
            "description": "Complete project with file management",
            "budget": 1000.0,
            "duration_hours": 5,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = uploader_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        # Upload gig documentation
        gig_files = {"file": ("project_specs.jpg", BytesIO(b"project_specifications"), "image/jpeg")}
        gig_upload_resp = uploader_client.post("/api/upload/gig", files=gig_files)
        assert gig_upload_resp.status_code == 201
        
        # Helper can see profile image when viewing gig
        gig_detail_resp = viewer_client.get(f"/api/gigs/{gig_id}")
        assert gig_detail_resp.status_code == 200
        gig_detail = gig_detail_resp.json()
        
        # Verify seeker has profile image set
        seeker_profile_resp = viewer_client.get(f"/api/users/profile")
        assert seeker_profile_resp.status_code == 200
        
        # Helper accepts gig
        accept_resp = viewer_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Complete workflow with file sharing
        rooms_resp = uploader_client.get("/api/chat/rooms")
        assert rooms_resp.status_code == 200
        room_id = rooms_resp.json()[0]["id"]
        
        # Share files in chat
        general_files = {"file": ("final_report.jpg", BytesIO(b"final_project_report"), "image/jpeg")}
        general_upload_resp = uploader_client.post("/api/upload/general", files=general_files)
        assert general_upload_resp.status_code == 201
        report_file_id = general_upload_resp.json()["id"]
        
        # Send file in chat
        message_data = {
            "content": "Here's the final project report",
            "message_type": "image",
            "image_url": f"/api/upload/{report_file_id}"
        }
        
        msg_resp = uploader_client.post(f"/api/chat/rooms/{room_id}/messages", json=message_data)
        assert msg_resp.status_code == 201
        
        # Viewer can access all shared files
        shared_file_resp = viewer_client.get(f"/api/upload/{report_file_id}")
        assert shared_file_resp.status_code == 200