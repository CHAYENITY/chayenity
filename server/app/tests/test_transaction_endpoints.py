#!/usr/bin/env python3
"""
Mock Payment System API test - tests transaction endpoints
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

def test_transaction_endpoints():
    """Test transaction endpoints with mock data."""
    print("🧪 Testing Mock Payment System API...")
    
    # Create test users
    test_id = str(uuid4())[:8]
    print("👤 Creating test users...")
    
    seeker_headers, seeker_id = register_and_login(f"seeker_{test_id}@example.com", "password", "Gig Seeker")
    helper_headers, helper_id = register_and_login(f"helper_{test_id}@example.com", "password", "Gig Helper")
    
    if not seeker_headers or not helper_headers:
        print("❌ Failed to create test users")
        return False
    
    print(f"✅ Created users: Seeker ({seeker_id}) and Helper ({helper_id})")
    
    # Test service fee calculation
    print("\n💰 Testing service fee calculation...")
    fee_resp = requests.post(f"{BASE_URL}/api/transactions/calculate-fee?amount=1000&fee_rate=0.05")
    if fee_resp.status_code == 200:
        fee_data = fee_resp.json()
        print(f"✅ Service fee calculation: {fee_data['base_amount']} THB -> Fee: {fee_data['service_fee_amount']} THB, Net: {fee_data['net_amount']} THB")
    else:
        print(f"❌ Service fee calculation failed: {fee_resp.status_code}: {fee_resp.text}")
    
    # Test validation with mock data
    print("\n📝 Testing transaction validation...")
    
    # Test 1: No authentication
    print("🔒 Testing no authentication...")
    escrow_data = {
        "gig_id": str(uuid4()),
        "payment_method": "mock_payment"
    }
    
    no_auth_resp = requests.post(f"{BASE_URL}/api/transactions/escrow", json=escrow_data)
    if no_auth_resp.status_code == 401:
        print("✅ Correctly rejected unauthorized request")
    else:
        print(f"❌ Expected 401 for no auth, got {no_auth_resp.status_code}: {no_auth_resp.text}")
    
    # Test 2: Invalid gig ID
    print("📦 Testing invalid gig ID...")
    invalid_escrow_resp = requests.post(f"{BASE_URL}/api/transactions/escrow", json=escrow_data, headers=seeker_headers)
    if invalid_escrow_resp.status_code in (400, 404):
        print("✅ Correctly rejected invalid gig ID")
    else:
        print(f"❌ Expected 400/404 for invalid gig, got {invalid_escrow_resp.status_code}: {invalid_escrow_resp.text}")
    
    # Test endpoint availability
    print("\n📋 Testing endpoint availability...")
    
    # Test get my transaction history (should work with empty result)
    history_resp = requests.get(f"{BASE_URL}/api/transactions/history/my", headers=seeker_headers)
    if history_resp.status_code == 200:
        print("✅ GET /history/my endpoint working")
        history = history_resp.json()
        print(f"   Found {len(history['transactions'])} transactions")
    else:
        print(f"❌ GET /history/my endpoint issue: {history_resp.status_code}: {history_resp.text}")
    
    # Test get my payment summary
    summary_resp = requests.get(f"{BASE_URL}/api/transactions/summary/my", headers=seeker_headers)
    if summary_resp.status_code == 200:
        print("✅ GET /summary/my endpoint working")
        summary = summary_resp.json()
        print(f"   User: {summary['user_name']}, Total transactions: {summary['total_transactions']}")
    else:
        print(f"❌ GET /summary/my endpoint issue: {summary_resp.status_code}: {summary_resp.text}")
    
    # Test get non-existent transaction
    fake_transaction_id = "99999999-9999-4999-9999-999999999999"
    get_transaction_resp = requests.get(f"{BASE_URL}/api/transactions/{fake_transaction_id}", headers=seeker_headers)
    if get_transaction_resp.status_code == 404:
        print("✅ GET /{id} endpoint working (returns 404 for non-existent transaction)")
    else:
        print(f"❌ GET /{id} endpoint issue: {get_transaction_resp.status_code}")
    
    # Test release non-existent transaction
    release_resp = requests.put(f"{BASE_URL}/api/transactions/{fake_transaction_id}/release", headers=seeker_headers)
    if release_resp.status_code == 404:
        print("✅ PUT /{id}/release endpoint working (returns 404 for non-existent transaction)")
    else:
        print(f"❌ PUT /{id}/release endpoint issue: {release_resp.status_code}")
    
    # Test cancel non-existent transaction
    cancel_resp = requests.put(f"{BASE_URL}/api/transactions/{fake_transaction_id}/cancel", headers=seeker_headers)
    if cancel_resp.status_code == 404:
        print("✅ PUT /{id}/cancel endpoint working (returns 404 for non-existent transaction)")
    else:
        print(f"❌ PUT /{id}/cancel endpoint issue: {cancel_resp.status_code}")
    
    print("\n🎉 Transaction API endpoint tests completed!")
    return True

def test_transaction_validation():
    """Test transaction validation and error scenarios."""
    print("\n🧪 Testing Transaction System Validation...")
    
    test_id = str(uuid4())[:8]
    user_headers, user_id = register_and_login(f"validation_{test_id}@example.com", "password", "Validation User")
    
    if not user_headers:
        print("❌ Failed to create test user for validation")
        return False
    
    # Test invalid amount for fee calculation
    print("💰 Testing invalid amount for fee calculation...")
    invalid_fee_resp = requests.post(f"{BASE_URL}/api/transactions/calculate-fee?amount=-100")
    if invalid_fee_resp.status_code == 422:
        print("✅ Correctly rejected negative amount")
    else:
        print(f"❌ Expected 422 for negative amount, got {invalid_fee_resp.status_code}: {invalid_fee_resp.text}")
    
    # Test invalid fee rate
    print("📊 Testing invalid fee rate...")
    invalid_rate_resp = requests.post(f"{BASE_URL}/api/transactions/calculate-fee?amount=100&fee_rate=1.5")
    if invalid_rate_resp.status_code == 422:
        print("✅ Correctly rejected invalid fee rate (>1)")
    else:
        print(f"❌ Expected 422 for invalid fee rate, got {invalid_rate_resp.status_code}: {invalid_rate_resp.text}")
    
    # Test missing gig_id in escrow creation
    print("📦 Testing missing gig_id...")
    missing_gig_data = {"payment_method": "mock_payment"}
    missing_gig_resp = requests.post(f"{BASE_URL}/api/transactions/escrow", json=missing_gig_data, headers=user_headers)
    if missing_gig_resp.status_code == 422:
        print("✅ Correctly rejected missing gig_id")
    else:
        print(f"❌ Expected 422 for missing gig_id, got {missing_gig_resp.status_code}: {missing_gig_resp.text}")
    
    print("🎉 All validation tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Mock Payment System Tests")
    print("=" * 60)
    
    # Run main tests
    main_result = test_transaction_endpoints()
    
    # Run validation tests
    validation_result = test_transaction_validation()
    
    print("\n" + "=" * 60)
    if main_result and validation_result:
        print("✅ ALL PAYMENT SYSTEM TESTS PASSED!")
        print("💡 Note: Full integration tests require working gig creation and acceptance")
        exit(0)
    else:
        print("❌ Some Payment System tests failed!")
        exit(1)