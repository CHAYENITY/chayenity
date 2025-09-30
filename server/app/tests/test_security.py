import asyncio
import time
import types
import pytest
from datetime import timedelta
from jose import JWTError
from uuid import UUID

from app import security


def test_hash_and_verify_roundtrip():
    pw = "correct-horse-battery-staple"
    hashed = security.get_password_hash(pw)
    assert isinstance(hashed, str)
    assert security.verify_password(pw, hashed) is True
    assert security.verify_password("wrongpw", hashed) is False


def test_hash_salts_are_unique():
    pw = "same-password"
    h1 = security.get_password_hash(pw)
    h2 = security.get_password_hash(pw)
    assert h1 != h2  # salts should differ
    assert security.verify_password(pw, h1)
    assert security.verify_password(pw, h2)


def test_long_password_handling():
    pw = "x" * 200  # >72 bytes
    hashed = security.get_password_hash(pw)
    assert security.verify_password(pw, hashed) is True


def test_tokens_include_sub_and_exp():
    data = {"sub": "123e4567-e89b-12d3-a456-426614174000"}
    access = security.create_access_token(data)
    refresh = security.create_refresh_token(data)

    dec_access = security.jwt.decode(
        access, security.app_config.ACCESS_SECRET_KEY, algorithms=[security.app_config.ALGORITHM]
    )
    dec_refresh = security.jwt.decode(
        refresh, security.app_config.REFRESH_SECRET_KEY, algorithms=[security.app_config.ALGORITHM]
    )

    assert dec_access["sub"] == data["sub"]
    assert "exp" in dec_access
    assert dec_refresh["sub"] == data["sub"]
    assert "exp" in dec_refresh


def test_token_expiration_behavior():
    # create access token with very short TTL
    small_token = security.create_access_token({"sub": "a"}, expires_delta=timedelta(seconds=1))
    payload = security.jwt.decode(small_token, security.app_config.ACCESS_SECRET_KEY, algorithms=[security.app_config.ALGORITHM])
    assert "exp" in payload
    # wait until it's expired - give a safe margin to cross integer-second truncation
    time.sleep(2.1)
    with pytest.raises(JWTError):
        security.jwt.decode(small_token, security.app_config.ACCESS_SECRET_KEY, algorithms=[security.app_config.ALGORITHM])


def test_get_current_user_with_access_token_coerces_uuid_and_loads_user():
    # Build token with UUID string subject
    uid_str = "123e4567-e89b-12d3-a456-426614174000"
    token = security.create_access_token({"sub": uid_str})

    captured = {}

    class FakeSession:
        async def get(self, model, key):
            # capture the runtime type of key and return a dummy user
            captured['model'] = model
            captured['key'] = key
            user = types.SimpleNamespace(id=key, email="t@example.com")
            return user

    fake_db = FakeSession()
    # Call the dependency helper directly (it's async) using asyncio.run
    # runtime-only: fake_db implements async get; ignore static typing here
    user = asyncio.run(security.get_current_user_with_access_token(access_token=token, db=fake_db))  # type: ignore[arg-type]
    assert user.email == "t@example.com"
    # Ensure the key we passed to db.get was coerced to a UUID
    assert isinstance(captured['key'], UUID)
