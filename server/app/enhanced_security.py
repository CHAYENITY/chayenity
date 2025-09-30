# Enhanced Authentication with Token Rotation
# This addresses the critical security vulnerability: "If hacker steals both tokens, unlimited access"

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class UserSession(Base):
    """
    Track active user sessions for enhanced security.
    Allows token rotation and session management.
    """
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    refresh_token_jti = Column(String, nullable=False, unique=True)  # JWT ID for refresh token
    device_info = Column(String, nullable=True)  # User agent, device type
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Optional security features
    login_location = Column(String, nullable=True)  # City/Country
    is_suspicious = Column(Boolean, default=False)


class BlacklistedToken(Base):
    """
    Store blacklisted/revoked tokens for immediate invalidation.
    Critical for logout and security breaches.
    """
    __tablename__ = "blacklisted_tokens"
    
    jti = Column(String, primary_key=True)  # JWT ID
    token_type = Column(String, nullable=False)  # 'access' or 'refresh'
    user_id = Column(String, nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reason = Column(String, nullable=True)  # 'logout', 'security_breach', 'expired'
    expires_at = Column(DateTime, nullable=False)  # When to clean up this record


# Enhanced Security Functions

async def create_user_session(
    db: AsyncSession,
    user_id: str,
    refresh_token_jti: str,
    device_info: str = None,
    ip_address: str = None,
    expires_at: datetime = None
) -> UserSession:
    """Create a new user session record."""
    session = UserSession(
        user_id=user_id,
        refresh_token_jti=refresh_token_jti,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def invalidate_user_session(db: AsyncSession, refresh_token_jti: str) -> bool:
    """Invalidate a specific user session."""
    result = await db.execute(
        update(UserSession)
        .where(UserSession.refresh_token_jti == refresh_token_jti)
        .values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0


async def get_active_user_sessions(db: AsyncSession, user_id: str) -> list[UserSession]:
    """Get all active sessions for a user."""
    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == user_id)
        .where(UserSession.is_active == True)
        .where(UserSession.expires_at > datetime.now(timezone.utc))
    )
    return result.scalars().all()


async def blacklist_token(
    db: AsyncSession,
    jti: str,
    token_type: str,
    user_id: str,
    reason: str = "logout",
    expires_at: datetime = None
) -> BlacklistedToken:
    """Add token to blacklist for immediate invalidation."""
    blacklisted = BlacklistedToken(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        reason=reason,
        expires_at=expires_at
    )
    db.add(blacklisted)
    await db.commit()
    return blacklisted


async def is_token_blacklisted(db: AsyncSession, jti: str) -> bool:
    """Check if token is blacklisted."""
    result = await db.execute(
        select(BlacklistedToken)
        .where(BlacklistedToken.jti == jti)
        .where(BlacklistedToken.expires_at > datetime.now(timezone.utc))
    )
    return result.scalar_one_or_none() is not None


# Enhanced Token Creation with JTI (JWT ID)

def create_access_token_with_jti(data: dict, expires_delta: timedelta = None) -> tuple[str, str]:
    """Create access token with unique JTI for tracking."""
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE)
    
    to_encode.update({
        "exp": expire,
        "jti": jti,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        app_config.ACCESS_SECRET_KEY, 
        algorithm=app_config.ALGORITHM
    )
    
    return encoded_jwt, jti


def create_refresh_token_with_jti(data: dict, expires_delta: timedelta = None) -> tuple[str, str]:
    """Create refresh token with unique JTI for tracking."""
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=app_config.REFRESH_TOKEN_EXPIRE)
    
    to_encode.update({
        "exp": expire,
        "jti": jti,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        app_config.REFRESH_SECRET_KEY, 
        algorithm=app_config.ALGORITHM
    )
    
    return encoded_jwt, jti


# Security Middleware

async def verify_token_not_blacklisted(token: str, secret_key: str, db: AsyncSession) -> dict:
    """Verify token is not blacklisted and return payload."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[app_config.ALGORITHM])
        jti = payload.get("jti")
        
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing JTI (security identifier)"
            )
        
        # Check if token is blacklisted
        if await is_token_blacklisted(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# Rate Limiting for Refresh Endpoint
from collections import defaultdict
from datetime import datetime, timedelta

# In-memory rate limiting (use Redis in production)
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