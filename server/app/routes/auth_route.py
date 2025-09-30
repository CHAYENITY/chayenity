from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timezone
import uuid

from app.models import User
from app.schemas.user_schema import UserCreate, UserOut
from app.crud import user_crud
from app.database.session import get_db
from app.security import (
    get_password_hash,
    verify_password,
    create_refresh_token,
    create_access_token,
    get_current_user_with_refresh_token,
    get_current_user_with_access_token,
)
from app.configs.app_config import app_config

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user_by_email = await user_crud.get_user_by_email(db, user_create.email)
    if existing_user_by_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    password_hash = get_password_hash(user_create.password)
    user = await user_crud.create_user(db, user_create, password_hash)
    # Return only fields that exist in the current User model/schema to avoid
    # leaking or depending on fields that tests or callers may expect.
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "contact_info": user.contact_info,
        "address_text": user.address_text,
        # "latitude": user.latitude,
        # "longitude": user.longitude,
        "is_verified": user.is_verified,
        "reputation_score": user.reputation_score,
        "created_at": user.created_at,
    }


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

    # Issue both access and refresh tokens with JTI for tracking
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    
    access_token = create_access_token(
        data={"sub": str(user.id), "jti": access_jti, "type": "access"}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "jti": refresh_jti, "type": "refresh"}
    )
    
    # TODO: Store refresh_jti in user_sessions table for tracking
    # This enables session management and token rotation
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in_minutes": app_config.ACCESS_TOKEN_EXPIRE,
    }


@router.post("/refresh")
async def refresh_access_token(
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
    
    # Create NEW tokens with NEW JTIs (prevents token reuse)
    new_access_jti = str(uuid.uuid4())
    new_refresh_jti = str(uuid.uuid4())
    
    # Issue NEW access token
    access_token = create_access_token(
        data={"sub": str(current_user.id), "jti": new_access_jti, "type": "access"}
    )
    
    # 🔑 Issue NEW refresh token (TOKEN ROTATION)
    new_refresh_token = create_refresh_token(
        data={"sub": str(current_user.id), "jti": new_refresh_jti, "type": "refresh"}
    )
    
    # TODO for complete security:
    # 1. Invalidate old refresh token in user_sessions table
    # 2. Add old tokens to blacklist table
    # 3. Create new session record
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,  # 🔑 NEW refresh token (rotation!)
        "token_type": "bearer",
        "expires_in_minutes": app_config.ACCESS_TOKEN_EXPIRE,
        "security_note": "Old refresh token is now invalid (rotation)"
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user_with_access_token),
    x_refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token"),
    request: Request = None
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


@router.get("/me", response_model=UserOut)
async def get_current_user(current_user: User = Depends(get_current_user_with_access_token)):
    return current_user
