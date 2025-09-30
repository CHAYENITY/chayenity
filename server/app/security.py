
# security.py
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, select, update
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
import hashlib
import uuid

from app.database.session import get_db
from app.models import User
from app.configs.app_config import app_config
from uuid import UUID as _UUID


# 🛡️ ENHANCED SECURITY MODELS (for database integration)
# Note: These should be added to your models.py file for proper database setup

"""
Add these models to your app/models.py:

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    refresh_token_jti = Column(String, nullable=False, unique=True)
    device_info = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    login_location = Column(String, nullable=True)
    is_suspicious = Column(Boolean, default=False)

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    
    jti = Column(String, primary_key=True)
    token_type = Column(String, nullable=False)
    user_id = Column(String, nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reason = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)
"""

# 🔒 RATE LIMITING for Refresh Endpoint
refresh_attempts = defaultdict(list)
MAX_REFRESH_ATTEMPTS = 5  # Max attempts per IP per hour
RATE_LIMIT_WINDOW = timedelta(hours=1)

def check_refresh_rate_limit(ip_address: str) -> bool:
    """Check if IP has exceeded refresh rate limits."""
    now = datetime.now(timezone.utc)
    cutoff = now - RATE_LIMIT_WINDOW
    
    # Clean old attempts
    refresh_attempts[ip_address] = [
        attempt for attempt in refresh_attempts[ip_address] 
        if attempt > cutoff
    ]
    
    # Check if under limit
    if len(refresh_attempts[ip_address]) >= MAX_REFRESH_ATTEMPTS:
        return False
    
    # Record this attempt
    refresh_attempts[ip_address].append(now)
    return True


# Helper to ensure input is bytes for bcrypt APIs
def _to_bytes(s: str | bytes) -> bytes:
    return s.encode("utf-8") if isinstance(s, str) else s


def _normalize_password_bytes(pw_bytes: bytes) -> bytes:
    """Normalize password bytes to something bcrypt can accept.

    bcrypt has a 72-byte input limit. To avoid truncation or ValueError with
    long inputs, pre-hash inputs longer than 72 bytes using SHA-256 and use
    the hex digest bytes as the input to bcrypt. For short inputs, use the
    original bytes so bcrypt's salting remains effective.
    """
    if len(pw_bytes) > 72:
        # SHA-256 digest hex length is 64 characters (64 bytes when utf-8 encoded)
        return hashlib.sha256(pw_bytes).hexdigest().encode("utf-8")
    return pw_bytes


# Use bcrypt directly for hashing and verification. This avoids relying on
# Passlib (which is unmaintained and has compatibility issues with newer
# bcrypt releases). We return encoded UTF-8 strings for storage in the DB.
def get_password_hash(password: str) -> str:
    pwb = _to_bytes(password)
    pwb = _normalize_password_bytes(pwb)
    hashed = bcrypt.hashpw(pwb, bcrypt.gensalt())
    return hashed.decode("utf-8")


def get_pin_hash(pin: str) -> str:
    pwb = _to_bytes(pin)
    pwb = _normalize_password_bytes(pwb)
    hashed = bcrypt.hashpw(pwb, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        pwb = _to_bytes(plain_password)
        pwb = _normalize_password_bytes(pwb)
        return bcrypt.checkpw(pwb, _to_bytes(password_hash))
    except Exception:
        return False


def verify_pin(plain_pin: str, pin_hash: str) -> bool:
    try:
        pwb = _to_bytes(plain_pin)
        pwb = _normalize_password_bytes(pwb)
        return bcrypt.checkpw(pwb, _to_bytes(pin_hash))
    except Exception:
        return False


refresh_token_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
access_token_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")



def create_refresh_token(
    data: dict, expires_delta: timedelta = timedelta(days=app_config.REFRESH_TOKEN_EXPIRE)
) -> str:
    """Create refresh token (legacy version without JTI)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    # encode exp as int UTC timestamp to ensure consistent behaviour
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, app_config.REFRESH_SECRET_KEY, algorithm=app_config.ALGORITHM)


def create_refresh_token_with_jti(
    data: dict, expires_delta: Optional[timedelta] = None
) -> tuple[str, str]:
    """🔑 Enhanced: Create refresh token with JTI for token rotation security."""
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.REFRESH_TOKEN_EXPIRE)
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "jti": jti,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        app_config.REFRESH_SECRET_KEY, 
        algorithm=app_config.ALGORITHM
    )
    
    return encoded_jwt, jti


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE),
) -> str:
    """Create access token (legacy version without JTI)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    # encode exp as int UTC timestamp to ensure consistent behaviour
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, app_config.ACCESS_SECRET_KEY, algorithm=app_config.ALGORITHM)


def create_access_token_with_jti(
    data: dict, expires_delta: Optional[timedelta] = None
) -> tuple[str, str]:
    """🔑 Enhanced: Create access token with JTI for tracking and security."""
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE)
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "jti": jti,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        app_config.ACCESS_SECRET_KEY, 
        algorithm=app_config.ALGORITHM
    )
    
    return encoded_jwt, jti


def decode_access_token(token: str) -> dict:
    """Decode and validate access token, return payload"""
    try:
        payload = jwt.decode(
            token, app_config.ACCESS_SECRET_KEY, algorithms=[app_config.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user_with_refresh_token(
    refresh_token: str = Depends(refresh_token_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            refresh_token,
            app_config.REFRESH_SECRET_KEY,
            algorithms=[app_config.ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # coerce to UUID where possible so DB comparisons match column type
        try:
            user_id = _UUID(user_id)
        except Exception:
            # leave as-is (fallback to string) if it isn't a UUID
            pass
    except JWTError:
        raise credentials_exception

    # AsyncSession.get handles primary-key lookups and accepts UUID or str
    user = await db.get(User, user_id)

    if user is None:
        raise credentials_exception
    return user


async def get_current_user_with_access_token(
    access_token: str = Depends(access_token_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            access_token, app_config.ACCESS_SECRET_KEY, algorithms=[app_config.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # coerce to UUID where possible so DB comparisons match column type
        try:
            user_id = _UUID(user_id)
        except Exception:
            pass
    except JWTError:
        raise credentials_exception

    # AsyncSession.get handles primary-key lookups and accepts UUID or str
    user = await db.get(User, user_id)

    if user is None:
        raise credentials_exception
    return user
