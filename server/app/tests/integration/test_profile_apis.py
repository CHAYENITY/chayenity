#!/usr/bin/env python3
"""Simple test script for User Profile Management APIs"""

import requests
import json

def test_apis():
    print('🎯 Testing User Profile Management APIs')
    print('==========================================')
    
    base_url = 'http://127.0.0.1:8000'
    
    # Test authentication first
    print('\n🔐 Testing Authentication...')
    login_data = {
        'username': 'test@example.com',
        'password': 'password'
    }
    
    try:
        response = requests.post(f'{base_url}/api/auth/login', data=login_data)
        if response.status_code == 200:
            token = response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            print('✅ Successfully authenticated')
        else:
            print(f'❌ Authentication failed: {response.status_code} - {response.text}')
            return False
            
        # Test get current profile
        print('\n👤 Testing Get Current Profile...')
        response = requests.get(f'{base_url}/api/users/profile', headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f'✅ Successfully retrieved profile: {profile["full_name"]}')
            print(f'  - Has location: {profile["has_location"]}')
            print(f'  - Is available: {profile["is_available"]}')
        else:
            print(f'❌ Profile get failed: {response.status_code} - {response.text}')
            
        # Test location update
        print('\n📍 Testing Location Update...')
        location_data = {
            'latitude': 13.7563,
            'longitude': 100.5018,
            'address_text': 'Bangkok, Thailand - API Test'
        }
        
        response = requests.put(f'{base_url}/api/users/location', json=location_data, headers=headers)
        if response.status_code == 200:
            print('✅ Successfully updated user location')
            
            # Verify location was set
            profile_response = requests.get(f'{base_url}/api/users/profile', headers=headers)
            if profile_response.status_code == 200:
                updated_profile = profile_response.json()
                if updated_profile['has_location']:
                    print('✅ Location update confirmed - has_location is now true')
                else:
                    print('❌ Location update failed - has_location is still false')
                    
                    # Debug the location data
                    debug_response = requests.get(f'{base_url}/api/users/debug-location', headers=headers)
                    if debug_response.status_code == 200:
                        debug_data = debug_response.json()
                        print(f'  🔍 Debug info: {debug_data}')
            else:
                print(f'❌ Profile verification failed: {profile_response.status_code}')
        else:
            print(f'❌ Location update failed: {response.status_code} - {response.text}')
            
        # Test availability toggle
        print('\n🟢 Testing Availability Toggle...')
        availability_data = {'is_available': True}
        
        response = requests.put(f'{base_url}/api/users/availability', json=availability_data, headers=headers)
        if response.status_code == 200:
            print('✅ Successfully updated availability to True')
            
            # Toggle off
            availability_data = {'is_available': False}
            response = requests.put(f'{base_url}/api/users/availability', json=availability_data, headers=headers)
            if response.status_code == 200:
                print('✅ Successfully toggled availability to False')
            else:
                print(f'❌ Availability toggle off failed: {response.status_code}')
        else:
            print(f'❌ Availability update failed: {response.status_code} - {response.text}')
            
        # Test nearby helpers search (requires helpers in database)
        print('\n🔍 Testing Nearby Helpers Search...')
        search_params = {
            'latitude': 13.7563,
            'longitude': 100.5018,
            'radius': 50.0,
            'only_available': True
        }
        
        response = requests.get(f'{base_url}/api/users/nearby', params=search_params, headers=headers)
        if response.status_code == 200:
            nearby_helpers = response.json()
            print(f'✅ Successfully found {len(nearby_helpers)} available helpers within 50km')
            for helper in nearby_helpers[:3]:  # Show first 3
                print(f'  - {helper["full_name"]}: {helper["distance_km"]}km away')
        else:
            print(f'❌ Nearby search failed: {response.status_code} - {response.text}')
            
        print('\n🎉 User Profile Management APIs Test Complete!')
        return True
        
    except Exception as e:
        print(f'❌ Test error: {e}')
        return False

if __name__ == "__main__":
    test_apis()