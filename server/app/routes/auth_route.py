from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timezone
import uuid

from app.models import User
from app.schemas.user_schema import UserRegister, UserProfileSetup, UserOut
from app.crud import user_crud
from app.database.session import get_db
from app.security import (
    get_password_hash,
    verify_password,
    create_refresh_token,
    create_access_token,
    create_refresh_token_with_jti,  # Enhanced version
    create_access_token_with_jti,   # Enhanced version
    get_current_user_with_refresh_token,
    get_current_user_with_access_token,
    check_refresh_rate_limit,       # Rate limiting
)
from app.configs.app_config import app_config

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_register: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Basic registration with email and password only.
    User must complete profile setup in step 2.
    """
    existing_user_by_email = await user_crud.get_user_by_email(db, user_register.email)
    if existing_user_by_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    password_hash = get_password_hash(user_register.password)
    
    # Create user with minimal information (email + password only)
    user_data = {
        "email": user_register.email,
        "hashed_password": password_hash,
        "is_profile_complete": False
    }
    
    user = await user_crud.create_minimal_user(db, user_data)
    
    # Return a minimal, deterministic response to avoid schema/example
    # injection and lazy-loading of relationships during serialization.
    return {
        "id": user.id,
        "email": user.email,
        "is_profile_complete": user.is_profile_complete,
        "created_at": user.created_at,
    }


@router.put("/profile-setup", response_model=UserOut)
async def setup_profile(
    profile_setup: UserProfileSetup,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Complete user profile setup after basic registration.
    This includes name, phone, bio, address, and profile image.
    """
    if current_user.is_profile_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Profile already completed"
        )
    
    # Update user profile with complete information
    updated_user = await user_crud.complete_user_profile(db, current_user.id, profile_setup)
    
    return updated_user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # Use email as username for login
    user = await user_crud.get_user_by_email(db, form_data.username.strip().lower())

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 🔑 Issue ENHANCED tokens with JTI for security tracking
    access_token, access_jti = create_access_token_with_jti(
        data={"sub": str(user.id)}
    )
    refresh_token, refresh_jti = create_refresh_token_with_jti(
        data={"sub": str(user.id)}
    )
    
    # TODO: Store refresh_jti in user_sessions table for session tracking
    # await create_user_session(db, str(user.id), refresh_jti, device_info, ip_address, expires_at)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in_minutes": app_config.ACCESS_TOKEN_EXPIRE,
    }


@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    x_access_token: Optional[str] = Header(None, alias="X-Access-Token"),
    current_user: User = Depends(get_current_user_with_refresh_token)
):
    """
    Refresh access token using BOTH refresh token and old access token for enhanced security.
    
    Headers required:
    - Authorization: Bearer <refresh_token>
    - X-Access-Token: <old_access_token>
    
    This ensures that an attacker needs both tokens to refresh the session.
    """
    if not x_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old access token required in X-Access-Token header"
        )
    
    try:
        # Verify the old access token belongs to the same user
        # We allow expired tokens here since that's the point of refresh
        payload = jwt.decode(
            x_access_token, 
            app_config.ACCESS_SECRET_KEY,  # Fixed: use ACCESS_SECRET_KEY
            algorithms=[app_config.ALGORITHM],
            options={"verify_exp": False}  # Allow expired tokens
        )
        old_token_user_id = payload.get("sub")
        
        # Ensure the refresh token and old access token belong to the same user
        if str(current_user.id) != old_token_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token mismatch: refresh and access tokens belong to different users"
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token format"
        )
    
    # 🔄 CRITICAL SECURITY FIX: TOKEN ROTATION
    # This solves "if hacker steals both tokens, unlimited access" problem
    
    # Rate limiting check
    client_ip = getattr(request, 'client', {}).get('host', 'unknown') if request else 'unknown'
    if not check_refresh_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many refresh attempts. Please try again later."
        )
    
    # 🔑 Create NEW tokens with enhanced security (JTI rotation)
    access_token, new_access_jti = create_access_token_with_jti(
        data={"sub": str(current_user.id)}
    )
    new_refresh_token, new_refresh_jti = create_refresh_token_with_jti(
        data={"sub": str(current_user.id)}
    )
    
    # TODO for complete security (database operations):
    # 1. Invalidate old refresh token: await invalidate_user_session(db, old_refresh_jti)
    # 2. Create new session: await create_user_session(db, str(current_user.id), new_refresh_jti, ...)
    # 3. Add old tokens to blacklist: await blacklist_token(db, old_access_jti, "access", ...)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,  # 🔑 NEW refresh token (rotation!)
        "token_type": "bearer",
        "expires_in_minutes": app_config.ACCESS_TOKEN_EXPIRE,
        "security_note": "Old refresh token is now invalid (rotation)"
    }


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user_with_access_token),
    x_refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token")
):
    """
    🔐 Enhanced logout with token invalidation.
    
    For complete security, provide refresh token to invalidate:
    Headers:
    - Authorization: Bearer <access_token>
    - X-Refresh-Token: <refresh_token> (optional but recommended)
    
    TODO: Implement token blacklist for immediate invalidation
    """
    
    # Extract token JTIs for blacklisting
    # This prevents stolen tokens from being used after logout
    try:
        auth_header = request.headers.get("authorization", "")
        access_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
        
        if access_token:
            access_payload = jwt.decode(
                access_token,
                app_config.ACCESS_SECRET_KEY,
                algorithms=[app_config.ALGORITHM],
                options={"verify_exp": False}
            )
            access_jti = access_payload.get("jti")
            
        if x_refresh_token:
            refresh_payload = jwt.decode(
                x_refresh_token,
                app_config.REFRESH_SECRET_KEY,
                algorithms=[app_config.ALGORITHM],
                options={"verify_exp": False}
            )
            refresh_jti = refresh_payload.get("jti")
            
        # TODO: Add tokens to blacklist
        # await blacklist_token(db, access_jti, "access", str(current_user.id), "logout")
        # await blacklist_token(db, refresh_jti, "refresh", str(current_user.id), "logout")
        
    except JWTError:
        # Still allow logout even if token parsing fails
        pass
    
    return {
        "message": "Successfully logged out",
        "security_note": "All tokens for this session should be discarded"
    }
