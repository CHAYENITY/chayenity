
# security.py
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import hashlib
import calendar

from app.database.session import get_db
from app.models import User
from app.configs.app_config import app_config
from uuid import UUID as _UUID


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
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    # encode exp as int UTC timestamp to ensure consistent behaviour
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, app_config.REFRESH_SECRET_KEY, algorithm=app_config.ALGORITHM)


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE),
) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    # encode exp as int UTC timestamp to ensure consistent behaviour
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, app_config.ACCESS_SECRET_KEY, algorithm=app_config.ALGORITHM)


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
