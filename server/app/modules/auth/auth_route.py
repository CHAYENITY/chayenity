# routes/auth_route.py
import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.api_schema import CreateOut
from app.database.session import get_db
from app.security import (
    get_password_hash,
    verify_password,
    create_refresh_token,
    create_access_token,
    get_current_user_with_refresh_token,
)

from app.modules.users.user_schema import UserCreate
from app.modules.users import user_crud


router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/register", response_model=CreateOut, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user_by_email = await user_crud.get_user_by_email(db, user_create.email)
    if existing_user_by_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_user_by_phone = await user_crud.get_user_by_phone_number(db, user_create.phone_number)
    if existing_user_by_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    hashed_password = get_password_hash(user_create.password)
    result = await user_crud.create_user(db, user_create, hashed_password)
    return result


@router.post("/login")
async def login(
    # * username = Email/ หมายเลขโทรศัพท์
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user: User | None = None
    input_identifier = form_data.username.strip().lower()

    # * Email
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", input_identifier):
        user = await user_crud.get_user_by_email(db, input_identifier)

    # * Phone Number
    elif input_identifier.isdigit():
        user = await user_crud.get_user_by_phone_number(db, input_identifier)

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
