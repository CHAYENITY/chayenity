# routes/auth_route.py
import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user_schema import UserCreate, UserOut, UserProfileSetup
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

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user_by_email = await user_crud.get_user_by_email(db, user_create.email)
    if existing_user_by_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed_password = get_password_hash(user_create.password)
    user = await user_crud.create_user(db, user_create, hashed_password)
    # Override addresses to [] to avoid lazy loading error
    return UserOut.model_validate({**user.__dict__, "addresses": []})


@router.post("/login")
async def login(
    # * username = Email
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user: User | None = None
    input_identifier = form_data.username.strip().lower()

    # * Email
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", input_identifier):
        user = await user_crud.get_user_by_email(db, input_identifier)

    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "refresh_token": refresh_token,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh(
    current_user: User = Depends(get_current_user_with_refresh_token),
):

    access_token = create_access_token(data={"sub": str(current_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.put("/profile-setup", response_model=UserOut)
async def setup_profile(
    profile_setup: UserProfileSetup,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2: Complete user profile setup after basic registration.
    This includes name, phone, bio, address, and profile image.
    """
    if current_user.is_profile_setup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already setup")

    # Update user profile with complete information
    await user_crud.create_user_profile(db, current_user.id, profile_setup)

    return UserOut.model_validate({**current_user.__dict__, "addresses": []})
