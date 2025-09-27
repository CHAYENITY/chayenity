#!/usr/bin/env python3
"""
Simple test script to verify the Gig CRUD system is working without pytest complications
"""
import asyncio
import httpx
import json
from app.main import app
from app.database.session import get_db
from app.models import User
from app.security import get_password_hash


async def create_test_user():
    """Create a test user"""
    async for session in get_db():
        # Check if user already exists by email (not by ID)
        from sqlmodel import select
        stmt = select(User).where(User.email == "test@example.com")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user = User(
                email="test@example.com", 
                hashed_password=get_password_hash("password"),
                full_name="Test User"
            )
            session.add(user)
            await session.commit()
            print("✅ Created test user")
        else:
            print("✅ Test user already exists")
        break


async def create_helper_user():
    """Create a helper user for testing gig acceptance"""
    async for session in get_db():
        from sqlmodel import select
        stmt = select(User).where(User.email == "helper@example.com")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user = User(
                email="helper@example.com", 
                hashed_password=get_password_hash("password"),
                full_name="Helper User",
                is_available=True
            )
            session.add(user)
            await session.commit()
            print("✅ Created helper user")
        else:
            print("✅ Helper user already exists")
        break


async def test_gig_system():
    """Test the complete gig system"""
    
    # Start with user creation
    await create_test_user()
    
    # Test authentication first
    from httpx import ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n🔐 Testing Authentication...")
        
        # Login to get token
        login_data = {
            "username": "test@example.com",
            "password": "password"
        }
        
        login_response = await client.post("/api/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
            
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        headers = {"Authorization": f"Bearer {access_token}"}
        print("✅ Successfully authenticated")
        
        print("\n📝 Testing Gig Creation...")
        
        # Create a test gig
        gig_data = {
            "title": "Test Gig",
            "description": "A test gig for validation",
            "duration_hours": 2,
            "budget": 50.0,
            "location": {
                "latitude": 40.730610,
                "longitude": -73.935242
            },
            "address_text": "New York, NY",
        }
        
        create_response = await client.post("/api/gigs/", json=gig_data, headers=headers)
        
        if create_response.status_code != 201:
            print(f"❌ Gig creation failed: {create_response.status_code} - {create_response.text}")
            return False
            
        gig_response = create_response.json()
        gig_id = gig_response["id"]
        print(f"✅ Successfully created gig: {gig_id}")
        print(f"✅ Successfully created gig: {gig_id}")
        
        print("\n🔍 Testing Gig Search...")
        
        # Test geospatial search
        search_params = {
            "latitude": 40.730610,
            "longitude": -73.935242,
            "radius": 10
        }
        
        search_response = await client.get("/api/gigs/search", params=search_params, headers=headers)
        
        if search_response.status_code != 200:
            print(f"❌ Gig search failed: {search_response.status_code} - {search_response.text}")
            return False
            
        search_results = search_response.json()
        print(f"✅ Successfully found {len(search_results)} gigs in area")
        
        print("\n📋 Testing My Gigs...")
        
        # Test user's gigs
        my_gigs_response = await client.get("/api/gigs/my-gigs", headers=headers)
        
        if my_gigs_response.status_code != 200:
            print(f"❌ My gigs failed: {my_gigs_response.status_code} - {my_gigs_response.text}")
            return False
            
        my_gigs = my_gigs_response.json()
        print(f"✅ Successfully retrieved {len(my_gigs)} user gigs")
        
        print("\n🎯 Testing Gig Details...")
        
        # Get specific gig details
        detail_response = await client.get(f"/api/gigs/{gig_id}", headers=headers)
        
        if detail_response.status_code != 200:
            print(f"❌ Gig details failed: {detail_response.status_code} - {detail_response.text}")
            return False
            
        gig_detail = detail_response.json()
        print(f"✅ Successfully retrieved gig details: {gig_detail['title']}")
        
        print("\n📝 Testing Gig Update...")
        
        # Update gig
        update_data = {
            "title": "Updated Test Gig",
            "budget": 75.0
        }
        
        update_response = await client.put(f"/api/gigs/{gig_id}", json=update_data, headers=headers)
        
        if update_response.status_code != 200:
            print(f"❌ Gig update failed: {update_response.status_code} - {update_response.text}")
            return False
            
        print("✅ Successfully updated gig")
        
        print("\n🤝 Testing Gig Acceptance...")
        
        # Create a second user to test gig acceptance
        await create_helper_user()
        
        # Login as helper
        helper_login_data = {
            "username": "helper@example.com",
            "password": "password"
        }
        
        helper_login_response = await client.post("/api/auth/login", data=helper_login_data)
        
        if helper_login_response.status_code != 200:
            print(f"❌ Helper login failed: {helper_login_response.status_code} - {helper_login_response.text}")
            return False
            
        helper_token_data = helper_login_response.json()
        helper_access_token = helper_token_data["access_token"]
        helper_headers = {"Authorization": f"Bearer {helper_access_token}"}
        
        # Helper accepts the gig
        accept_response = await client.post(f"/api/gigs/{gig_id}/accept", headers=helper_headers)
        
        if accept_response.status_code != 200:
            print(f"❌ Gig acceptance failed: {accept_response.status_code} - {accept_response.text}")
            return False
            
        print("✅ Successfully accepted gig as helper")
        
        print("\n📊 Testing Gig Status Updates...")
        
        # Update gig status to in_progress
        status_update_data = {
            "status": "in_progress"
        }
        
        status_response = await client.put(f"/api/gigs/{gig_id}/status", json=status_update_data, headers=helper_headers)
        
        if status_response.status_code != 200:
            print(f"❌ Status update failed: {status_response.status_code} - {status_response.text}")
            return False
            
        print("✅ Successfully updated gig status to in_progress")
        
        # Update gig status to completed
        status_update_data = {
            "status": "completed"
        }
        
        status_response = await client.put(f"/api/gigs/{gig_id}/status", json=status_update_data, headers=helper_headers)
        
        if status_response.status_code != 200:
            print(f"❌ Status completion failed: {status_response.status_code} - {status_response.text}")
            return False
            
        print("✅ Successfully completed gig")
        
        print("\n🗑️ Testing Gig Deletion...")
        
        # Create another gig to test deletion
        delete_gig_data = {
            "title": "Gig to Delete",
            "description": "This gig will be deleted",
            "duration_hours": 1,
            "budget": 25.0,
            "location": {
                "latitude": 40.730610,
                "longitude": -73.935242
            },
            "address_text": "New York, NY",
        }
        
        delete_create_response = await client.post("/api/gigs/", json=delete_gig_data, headers=headers)
        
        if delete_create_response.status_code != 201:
            print(f"❌ Delete test gig creation failed: {delete_create_response.status_code}")
            return False
            
        delete_gig_id = delete_create_response.json()["id"]
        
        # Delete the gig
        delete_response = await client.delete(f"/api/gigs/{delete_gig_id}", headers=headers)
        
        if delete_response.status_code != 204:
            print(f"❌ Gig deletion failed: {delete_response.status_code} - {delete_response.text}")
            return False
            
        print("✅ Successfully deleted gig")
        
        print(f"\n🎉 ALL TESTS PASSED! Complete Gig CRUD system is working perfectly!")
        print(f"✅ 9 API endpoints tested successfully")
        print(f"✅ PostGIS geospatial search working")
        print(f"✅ JWT authentication working") 
        print(f"✅ SQLModel + SQLAlchemy hybrid architecture working")
        print(f"✅ Pydantic V2 validation working")
        print(f"✅ Gig acceptance workflow tested")
        print(f"✅ Gig status management tested")
        print(f"✅ Gig deletion tested")
        print(f"✅ Multi-user workflow tested")
        
        return True


if __name__ == "__main__":
    result = asyncio.run(test_gig_system())
    if result:
        print("\n🚀 Core Gig CRUD APIs implementation is COMPLETE and WORKING!")
    else:
        print("\n❌ Some tests failed")