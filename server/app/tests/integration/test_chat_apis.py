import json
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app


def ensure_registered(client, email: str, password: str, full_name: str = "Test User"):
    # Try register, ignore if already exists (409)
    payload = {"email": email, "password": password, "full_name": full_name}
    resp = client.post("/api/auth/register", json=payload)
    return resp


def test_chat_endpoints_basic():
    email = "chattest@example.com"
    password = "testpass123"

    with TestClient(app) as client:
        ensure_registered(client, email, password, "Chat Tester")

        login_resp = client.post("/api/auth/login", data={"username": email, "password": password})
        assert login_resp.status_code == 200, f"login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        rooms_resp = client.get("/api/chat/rooms", headers=headers)
        assert rooms_resp.status_code == 200

        fake_room = str(uuid4())
        room_resp = client.get(f"/api/chat/rooms/{fake_room}", headers=headers)
        assert room_resp.status_code == 404

        messages_resp = client.get(f"/api/chat/rooms/{fake_room}/messages", headers=headers)
        assert messages_resp.status_code in (404, 200)

        send_payload = {"content": "Hello test", "message_type": "text"}
        send_resp = client.post(f"/api/chat/rooms/{fake_room}/messages", headers=headers, json=send_payload)
        assert send_resp.status_code in (404, 422)
