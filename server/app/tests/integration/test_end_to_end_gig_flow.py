"""
End-to-End Gig Flow Integration Tests

This module tests the complete gig workflow from creation to completion,
including payments, reviews, and all related functionality.

Tests cover:
- Complete gig lifecycle (create → accept → progress → complete)
- Payment escrow and release workflow
- Review system integration
- Chat room creation and messaging
- File uploads for gig images
- Multi-user interactions
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
import tempfile
import os
from io import BytesIO


class TestGigFlowEndToEnd:
    """Test complete end-to-end gig workflows"""

    @pytest.fixture
    def seeker_credentials(self):
        """Seeker user credentials"""
        return {
            "email": "seeker@example.com",
            "password": "seekerpass123",
            "full_name": "Gig Seeker",
            "name": "Seeker User"
        }

    @pytest.fixture
    def helper_credentials(self):
        """Helper user credentials"""
        return {
            "email": "helper@example.com", 
            "password": "helperpass123",
            "full_name": "Gig Helper",
            "name": "Helper User"
        }

    @pytest.fixture
    def seeker_client(self, seeker_credentials):
        """Authenticated client for seeker"""
        with TestClient(app) as client:
            # Register user
            client.post("/api/auth/register", json=seeker_credentials)
            
            # Login and get token
            login_resp = client.post("/api/auth/login", data={
                "username": seeker_credentials["email"],
                "password": seeker_credentials["password"]
            })
            token = login_resp.json()["access_token"]
            
            # Set location for seeker
            client.put("/api/users/location", 
                      headers={"Authorization": f"Bearer {token}"},
                      json={"latitude": 13.7563, "longitude": 100.5018})  # Bangkok
            
            client.headers.update({"Authorization": f"Bearer {token}"})
            yield client

    @pytest.fixture
    def helper_client(self, helper_credentials):
        """Authenticated client for helper"""
        with TestClient(app) as client:
            # Register user
            client.post("/api/auth/register", json=helper_credentials)
            
            # Login and get token
            login_resp = client.post("/api/auth/login", data={
                "username": helper_credentials["email"],
                "password": helper_credentials["password"]
            })
            token = login_resp.json()["access_token"]
            
            # Set location and availability for helper
            client.put("/api/users/location", 
                      headers={"Authorization": f"Bearer {token}"},
                      json={"latitude": 13.7563, "longitude": 100.5018})  # Bangkok
            client.put("/api/users/availability",
                      headers={"Authorization": f"Bearer {token}"},
                      json={"is_available": True})
            
            client.headers.update({"Authorization": f"Bearer {token}"})
            yield client

    def test_complete_gig_workflow_with_payment_and_review(self, seeker_client, helper_client):
        """Test complete gig workflow from creation to completion with payment and review"""
        
        # Step 1: Seeker creates a gig
        gig_data = {
            "title": "Help me move furniture",
            "description": "Need help moving a sofa and dining table to new apartment",
            "budget": 500.0,
            "duration_hours": 3,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = seeker_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201, f"Failed to create gig: {create_resp.text}"
        gig = create_resp.json()
        gig_id = gig["id"]
        
        assert gig["status"] == "PENDING"
        assert gig["title"] == gig_data["title"]
        assert gig["budget"] == gig_data["budget"]
        
        # Step 2: Helper searches for gigs and finds the created one
        search_resp = helper_client.get("/api/gigs/search?latitude=13.7563&longitude=100.5018&radius=10")
        assert search_resp.status_code == 200
        gigs = search_resp.json()
        assert len(gigs) >= 1
        
        found_gig = next((g for g in gigs if g["id"] == gig_id), None)
        assert found_gig is not None, "Created gig not found in search results"
        
        # Step 3: Helper accepts the gig
        accept_resp = helper_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200, f"Failed to accept gig: {accept_resp.text}"
        accepted_gig = accept_resp.json()
        assert accepted_gig["status"] == "ACCEPTED"
        assert accepted_gig["helper_id"] is not None
        
        # Step 4: Seeker creates escrow payment
        payment_data = {
            "gig_id": gig_id,
            "amount": gig_data["budget"]
        }
        escrow_resp = seeker_client.post("/api/transactions/escrow", json=payment_data)
        assert escrow_resp.status_code == 201, f"Failed to create escrow: {escrow_resp.text}"
        transaction = escrow_resp.json()
        transaction_id = transaction["id"]
        
        assert transaction["status"] == "PENDING"
        assert transaction["amount"] == gig_data["budget"]
        assert transaction["service_fee"] == gig_data["budget"] * 0.05  # 5% service fee
        
        # Step 5: Helper updates gig status to IN_PROGRESS
        progress_resp = helper_client.put(f"/api/gigs/{gig_id}/status", 
                                        json={"status": "IN_PROGRESS"})
        assert progress_resp.status_code == 200
        
        # Step 6: Helper marks gig as completed
        complete_resp = helper_client.put(f"/api/gigs/{gig_id}/status", 
                                        json={"status": "COMPLETED"})
        assert complete_resp.status_code == 200
        completed_gig = complete_resp.json()
        assert completed_gig["status"] == "COMPLETED"
        
        # Step 7: Seeker releases payment
        release_resp = seeker_client.put(f"/api/transactions/{transaction_id}/release")
        assert release_resp.status_code == 200, f"Failed to release payment: {release_resp.text}"
        released_transaction = release_resp.json()
        assert released_transaction["status"] == "COMPLETED"
        
        # Step 8: Both parties leave reviews
        # Seeker reviews helper
        seeker_review_data = {
            "gig_id": gig_id,
            "reviewee_id": completed_gig["helper_id"],
            "rating": 5,
            "comment": "Excellent work! Very professional and efficient."
        }
        seeker_review_resp = seeker_client.post("/api/reviews", json=seeker_review_data)
        assert seeker_review_resp.status_code == 201, f"Failed to create seeker review: {seeker_review_resp.text}"
        
        # Helper reviews seeker
        helper_review_data = {
            "gig_id": gig_id,
            "reviewee_id": completed_gig["seeker_id"],
            "rating": 4,
            "comment": "Great communication and clear instructions."
        }
        helper_review_resp = helper_client.post("/api/reviews", json=helper_review_data)
        assert helper_review_resp.status_code == 201, f"Failed to create helper review: {helper_review_resp.text}"
        
        # Step 9: Verify reviews were created and reputation updated
        gig_reviews_resp = seeker_client.get(f"/api/reviews/gig/{gig_id}")
        assert gig_reviews_resp.status_code == 200
        reviews = gig_reviews_resp.json()
        assert len(reviews) == 2
        
        # Step 10: Verify transaction history
        seeker_history_resp = seeker_client.get("/api/transactions/history/my")
        assert seeker_history_resp.status_code == 200
        seeker_transactions = seeker_history_resp.json()
        assert len(seeker_transactions) >= 1
        
        helper_history_resp = helper_client.get("/api/transactions/history/my")
        assert helper_history_resp.status_code == 200
        helper_transactions = helper_history_resp.json()
        assert len(helper_transactions) >= 1

    def test_gig_workflow_with_cancellation(self, seeker_client, helper_client):
        """Test gig workflow with cancellation and payment refund"""
        
        # Create gig
        gig_data = {
            "title": "Garden cleanup",
            "description": "Clean up backyard garden",
            "budget": 300.0,
            "duration_hours": 2,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = seeker_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        # Helper accepts gig
        accept_resp = helper_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Create escrow
        payment_data = {"gig_id": gig_id, "amount": gig_data["budget"]}
        escrow_resp = seeker_client.post("/api/transactions/escrow", json=payment_data)
        assert escrow_resp.status_code == 201
        transaction_id = escrow_resp.json()["id"]
        
        # Cancel transaction (refund)
        cancel_resp = seeker_client.put(f"/api/transactions/{transaction_id}/cancel")
        assert cancel_resp.status_code == 200
        cancelled_transaction = cancel_resp.json()
        assert cancelled_transaction["status"] == "CANCELLED"
        
        # Cancel gig
        cancel_gig_resp = seeker_client.put(f"/api/gigs/{gig_id}/status", 
                                           json={"status": "CANCELLED"})
        assert cancel_gig_resp.status_code == 200
        cancelled_gig = cancel_gig_resp.json()
        assert cancelled_gig["status"] == "CANCELLED"

    def test_gig_workflow_with_image_upload(self, seeker_client, helper_client):
        """Test gig workflow with image uploads"""
        
        # Create gig
        gig_data = {
            "title": "Photography session",
            "description": "Need professional photos taken",
            "budget": 800.0,
            "duration_hours": 2,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = seeker_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        # Upload gig image
        # Create a test image file
        image_content = b"fake_image_content_for_testing"
        files = {"file": ("test_gig_image.jpg", BytesIO(image_content), "image/jpeg")}
        
        upload_resp = seeker_client.post("/api/upload/gig", files=files)
        assert upload_resp.status_code == 201, f"Failed to upload gig image: {upload_resp.text}"
        uploaded_file = upload_resp.json()
        
        # Verify file was uploaded
        file_id = uploaded_file["id"]
        get_file_resp = seeker_client.get(f"/api/upload/{file_id}")
        assert get_file_resp.status_code == 200
        assert get_file_resp.headers["content-type"] == "image/jpeg"
        
        # Helper uploads profile image
        helper_image_content = b"helper_profile_image_content"
        helper_files = {"file": ("helper_profile.jpg", BytesIO(helper_image_content), "image/jpeg")}
        
        helper_upload_resp = helper_client.post("/api/upload/profile", files=helper_files)
        assert helper_upload_resp.status_code == 201
        
        # Helper accepts gig
        accept_resp = helper_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200

    def test_multiple_helpers_competing_for_gig(self, seeker_client, helper_credentials):
        """Test scenario where multiple helpers try to accept the same gig"""
        
        # Create additional helper clients
        helper2_creds = {
            "email": "helper2@example.com",
            "password": "helper2pass123",
            "full_name": "Second Helper",
            "name": "Helper Two"
        }
        
        helper3_creds = {
            "email": "helper3@example.com",
            "password": "helper3pass123",
            "full_name": "Third Helper",
            "name": "Helper Three"
        }
        
        # Create and setup helper clients
        with TestClient(app) as helper2_client:
            helper2_client.post("/api/auth/register", json=helper2_creds)
            login_resp2 = helper2_client.post("/api/auth/login", data={
                "username": helper2_creds["email"],
                "password": helper2_creds["password"]
            })
            token2 = login_resp2.json()["access_token"]
            helper2_client.headers.update({"Authorization": f"Bearer {token2}"})
            
            with TestClient(app) as helper3_client:
                helper3_client.post("/api/auth/register", json=helper3_creds)
                login_resp3 = helper3_client.post("/api/auth/login", data={
                    "username": helper3_creds["email"],
                    "password": helper3_creds["password"]
                })
                token3 = login_resp3.json()["access_token"]
                helper3_client.headers.update({"Authorization": f"Bearer {token3}"})
                
                # Create gig
                gig_data = {
                    "title": "Urgent delivery",
                    "description": "Need package delivered ASAP",
                    "budget": 200.0,
                    "duration_hours": 1,
                    "latitude": 13.7563,
                    "longitude": 100.5018
                }
                
                create_resp = seeker_client.post("/api/gigs", json=gig_data)
                assert create_resp.status_code == 201
                gig_id = create_resp.json()["id"]
                
                # First helper accepts gig
                accept_resp1 = helper2_client.post(f"/api/gigs/{gig_id}/accept")
                assert accept_resp1.status_code == 200
                
                # Second helper tries to accept the same gig (should fail)
                accept_resp2 = helper3_client.post(f"/api/gigs/{gig_id}/accept")
                assert accept_resp2.status_code == 400  # Already accepted
                
                # Verify gig status
                gig_detail_resp = seeker_client.get(f"/api/gigs/{gig_id}")
                assert gig_detail_resp.status_code == 200
                gig_detail = gig_detail_resp.json()
                assert gig_detail["status"] == "ACCEPTED"

    def test_buddy_system_integration_with_gig_flow(self, seeker_client, helper_client):
        """Test buddy system integration with gig workflow"""
        
        # Get helper user details
        helper_profile_resp = helper_client.get("/api/users/me")
        assert helper_profile_resp.status_code == 200
        helper_profile = helper_profile_resp.json()
        helper_id = helper_profile["id"]
        
        # Seeker adds helper to buddy list
        add_buddy_resp = seeker_client.post("/api/buddies", json={"buddy_id": helper_id})
        assert add_buddy_resp.status_code == 201
        
        # Create gig
        gig_data = {
            "title": "Regular cleaning service",
            "description": "Weekly apartment cleaning",
            "budget": 400.0,
            "duration_hours": 3,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = seeker_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        # Check if buddy is available
        available_buddies_resp = seeker_client.get("/api/buddies/available")
        assert available_buddies_resp.status_code == 200
        available_buddies = available_buddies_resp.json()
        
        # Helper should be in available buddies list
        buddy_ids = [buddy["buddy"]["id"] for buddy in available_buddies]
        assert helper_id in buddy_ids
        
        # Helper accepts gig from trusted seeker
        accept_resp = helper_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Complete the workflow
        escrow_resp = seeker_client.post("/api/transactions/escrow", 
                                       json={"gig_id": gig_id, "amount": gig_data["budget"]})
        assert escrow_resp.status_code == 201
        
        complete_resp = helper_client.put(f"/api/gigs/{gig_id}/status", 
                                        json={"status": "COMPLETED"})
        assert complete_resp.status_code == 200

    def test_chat_integration_with_gig_workflow(self, seeker_client, helper_client):
        """Test chat system integration with gig workflow"""
        
        # Create and accept gig
        gig_data = {
            "title": "Computer repair",
            "description": "Fix laptop screen",
            "budget": 600.0,
            "duration_hours": 2,
            "latitude": 13.7563,
            "longitude": 100.5018
        }
        
        create_resp = seeker_client.post("/api/gigs", json=gig_data)
        assert create_resp.status_code == 201
        gig_id = create_resp.json()["id"]
        
        accept_resp = helper_client.post(f"/api/gigs/{gig_id}/accept")
        assert accept_resp.status_code == 200
        
        # Check chat rooms - should have one for this gig
        rooms_resp = seeker_client.get("/api/chat/rooms")
        assert rooms_resp.status_code == 200
        rooms = rooms_resp.json()
        
        # Find the room for this gig
        gig_room = next((room for room in rooms if room["gig_id"] == gig_id), None)
        assert gig_room is not None, "Chat room not created for accepted gig"
        room_id = gig_room["id"]
        
        # Send messages between seeker and helper
        seeker_message = {
            "content": "Hi! When can you start the repair?",
            "message_type": "text"
        }
        
        seeker_msg_resp = seeker_client.post(f"/api/chat/rooms/{room_id}/messages", 
                                           json=seeker_message)
        assert seeker_msg_resp.status_code == 201
        
        helper_message = {
            "content": "I can start tomorrow morning at 9 AM. Is that good for you?",
            "message_type": "text"
        }
        
        helper_msg_resp = helper_client.post(f"/api/chat/rooms/{room_id}/messages", 
                                           json=helper_message)
        assert helper_msg_resp.status_code == 201
        
        # Get message history
        history_resp = seeker_client.get(f"/api/chat/rooms/{room_id}/messages")
        assert history_resp.status_code == 200
        messages = history_resp.json()
        assert len(messages) >= 2
        
        # Mark messages as read
        read_resp = helper_client.put(f"/api/chat/rooms/{room_id}/read")
        assert read_resp.status_code == 200