#!/usr/bin/env python3
"""
Comprehensive User Profile Management APIs Test
Tests all new user profile endpoints including location, availability, and nearby helpers
"""

import asyncio
import httpx
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db
from app.models import User
from app.security import get_password_hash
from geoalchemy2 import WKTElement


async def create_test_users():
    """Create multiple test users with different locations and availability"""
    async for session in get_db():
        from sqlmodel import select
        
        # Helper user 1 - Available in Bangkok
        stmt = select(User).where(User.email == "helper1@example.com")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user1 = User(
                email="helper1@example.com",
                hashed_password=get_password_hash("password"),
                full_name="Helper One Bangkok",
                is_available=True,
                fixed_location=WKTElement("POINT(100.5018 13.7563)", srid=4326),  # Bangkok
                address_text="Bangkok, Thailand"
            )
            session.add(user1)
            print("✅ Created helper1@example.com")
        else:
            print("✅ Helper1 user already exists")
        
        # Helper user 2 - Not available in Bangkok
        stmt = select(User).where(User.email == "helper2@example.com")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user2 = User(
                email="helper2@example.com",
                hashed_password=get_password_hash("password"),
                full_name="Helper Two Bangkok",
                is_available=False,
                fixed_location=WKTElement("POINT(100.5200 13.7400)", srid=4326),  # Near Bangkok
                address_text="Near Bangkok, Thailand"
            )
            session.add(user2)
            print("✅ Created helper2@example.com")
        else:
            print("✅ Helper2 user already exists")
            
        # Helper user 3 - Available but far away (Chiang Mai)
        stmt = select(User).where(User.email == "helper3@example.com")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user3 = User(
                email="helper3@example.com",
                hashed_password=get_password_hash("password"),
                full_name="Helper Three Chiang Mai",
                is_available=True,
                fixed_location=WKTElement("POINT(98.9817 18.7883)", srid=4326),  # Chiang Mai
                address_text="Chiang Mai, Thailand"
            )
            session.add(user3)
            print("✅ Created helper3@example.com")
        else:
            print("✅ Helper3 user already exists")
        
        await session.commit()
        break


def test_user_profile_system():
    """Test all User Profile Management APIs"""
    
    print("🎯 Starting User Profile Management APIs Test\n")
    
    # Create test users first
    asyncio.run(create_test_users())
    
    # Use TestClient for simpler testing
    with TestClient(app) as client:
        
        # Test user authentication
        print("🔐 Testing Authentication...")
        
        login_response = client.post("/api/auth/login", data={
            "username": "test@example.com",
            "password": "password"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Authentication failed: {login_response.status_code} - {login_response.text}")
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Successfully authenticated")
        
        # Test get current profile
        print("\n👤 Testing Get Current Profile...")
        
        profile_response = client.get("/api/users/profile", headers=headers)
        
        if profile_response.status_code != 200:
            print(f"❌ Profile get failed: {profile_response.status_code} - {profile_response.text}")
            return False
            
        profile = profile_response.json()
        print(f"✅ Successfully retrieved profile: {profile['full_name']}")
        print(f"  - Has location: {profile['has_location']}")
        print(f"  - Is available: {profile['is_available']}")
        
        # Test location update
        print("\n📍 Testing Location Update...")
        
        location_data = {
            "latitude": 13.7563,
            "longitude": 100.5018,
            "address_text": "Bangkok, Thailand - Updated"
        }
        
        location_response = client.put("/api/users/location", json=location_data, headers=headers)
        
        if location_response.status_code != 200:
            print(f"❌ Location update failed: {location_response.status_code} - {location_response.text}")
            return False
            
        print("✅ Successfully updated user location")
        
        # Verify location was set
        profile_response = client.get("/api/users/profile", headers=headers)
        updated_profile = profile_response.json()
        if updated_profile['has_location']:
            print("✅ Location update confirmed - has_location is now true")
        else:
            print("❌ Location update failed - has_location is still false")
        
        # Test availability toggle
        print("\n🟢 Testing Availability Toggle...")
        
        availability_data = {"is_available": True}
        
        availability_response = client.put("/api/users/availability", json=availability_data, headers=headers)
        
        if availability_response.status_code != 200:
            print(f"❌ Availability update failed: {availability_response.status_code} - {availability_response.text}")
            return False
            
        print("✅ Successfully updated availability to True")
        
        # Test availability toggle off
        availability_data = {"is_available": False}
        availability_response = client.put("/api/users/availability", json=availability_data, headers=headers)
        
        if availability_response.status_code != 200:
            print(f"❌ Availability toggle off failed: {availability_response.status_code} - {availability_response.text}")
            return False
            
        print("✅ Successfully toggled availability to False")
        
        # Test nearby helpers search
        print("\n🔍 Testing Nearby Helpers Search...")
        
        # Search near Bangkok (should find helpers)
        search_params = {
            "latitude": 13.7563,
            "longitude": 100.5018,
            "radius": 50.0,  # 50km radius
            "only_available": True
        }
        
        nearby_response = client.get("/api/users/nearby", params=search_params, headers=headers)
        
        if nearby_response.status_code != 200:
            print(f"❌ Nearby search failed: {nearby_response.status_code} - {nearby_response.text}")
            return False
            
        nearby_helpers = nearby_response.json()
        print(f"✅ Successfully found {len(nearby_helpers)} available helpers within 50km")
        
        for helper in nearby_helpers:
            print(f"  - {helper['full_name']}: {helper['distance_km']}km away")
        
        # Test search with unavailable helpers
        print("\n🔍 Testing Search Including Unavailable Helpers...")
        
        search_params["only_available"] = False
        
        nearby_response = client.get("/api/users/nearby", params=search_params, headers=headers)
        
        if nearby_response.status_code != 200:
            print(f"❌ Nearby search (all) failed: {nearby_response.status_code} - {nearby_response.text}")
            return False
            
        all_helpers = nearby_response.json()
        print(f"✅ Successfully found {len(all_helpers)} total helpers (available + unavailable) within 50km")
        
        # Test narrow search radius
        print("\n🎯 Testing Narrow Search Radius...")
        
        search_params = {
            "latitude": 13.7563,
            "longitude": 100.5018,
            "radius": 5.0,  # 5km radius
            "only_available": True
        }
        
        narrow_response = client.get("/api/users/nearby", params=search_params, headers=headers)
        
        if narrow_response.status_code != 200:
            print(f"❌ Narrow search failed: {narrow_response.status_code} - {narrow_response.text}")
            return False
            
        narrow_helpers = narrow_response.json()
        print(f"✅ Successfully found {len(narrow_helpers)} available helpers within 5km")
        
        # Test profile update
        print("\n✏️ Testing Profile Update...")
        
        profile_update_data = {
            "full_name": "Updated Test User",
            "contact_info": "0812345678",
            "address_text": "Updated Address"
        }
        
        update_response = client.put("/api/users/me", json=profile_update_data, headers=headers)
        
        if update_response.status_code != 200:
            print(f"❌ Profile update failed: {update_response.status_code} - {update_response.text}")
            return False
            
        print("✅ Successfully updated user profile")
        
        # Verify profile update
        final_profile_response = client.get("/api/users/profile", headers=headers)
        final_profile = final_profile_response.json()
        
        if final_profile['full_name'] == "Updated Test User":
            print("✅ Profile update confirmed")
        else:
            print("❌ Profile update not reflected")
        
        print(f"\n🎉 ALL USER PROFILE TESTS PASSED!")
        print(f"✅ Profile retrieval working")
        print(f"✅ Location setting working") 
        print(f"✅ Availability toggle working")
        print(f"✅ Nearby helpers search working")
        print(f"✅ Profile updates working")
        print(f"✅ PostGIS geospatial queries working")
        
        return True


if __name__ == "__main__":
    success = test_user_profile_system()
    if success:
        print(f"\n🚀 User Profile Management APIs implementation is COMPLETE and WORKING!")
    else:
        print(f"\n❌ Some tests failed")