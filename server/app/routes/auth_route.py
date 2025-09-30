from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

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

    # Issue both access and refresh tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in_minutes": app_config.ACCESS_TOKEN_EXPIRE,
    }


@router.get("/me", response_model=UserOut)
async def get_current_user(current_user: User = Depends(get_current_user_with_access_token)):
    return current_user
