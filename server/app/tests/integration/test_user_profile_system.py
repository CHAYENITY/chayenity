import json
from fastapi.testclient import TestClient
from app.main import app


def register_user(client, email: str, password: str, full_name: str = "Test User"):
    payload = {"email": email, "password": password, "full_name": full_name}
    resp = client.post("/api/auth/register", json=payload)
    return resp


def test_profile_endpoints_create_and_auth():
    with TestClient(app) as client:
        # Register users via the API so dependency override and DB session are used correctly
        register_user(client, "test@example.com", "password")
        register_user(client, "helper1@example.com", "password")
        register_user(client, "helper2@example.com", "password")
        register_user(client, "helper3@example.com", "password")

        # Login
        login_resp = client.post("/api/auth/login", data={"username": "test@example.com", "password": "password"})
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get profile
        profile_resp = client.get("/api/users/profile", headers=headers)
        assert profile_resp.status_code == 200
        profile = profile_resp.json()
        assert "email" in profile and profile["email"] == "test@example.com"

        # Update availability
        avail_resp = client.put("/api/users/availability", headers=headers, json={"is_available": True})
        assert avail_resp.status_code == 200

        # Nearby search
        params = {"latitude": 13.7563, "longitude": 100.5018, "radius": 50.0, "only_available": True}
        nearby_resp = client.get("/api/users/nearby", params=params, headers=headers)
        assert nearby_resp.status_code == 200
