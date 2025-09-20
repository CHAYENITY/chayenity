from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user_schema import UserOut, UserUpdate
from app.crud import user_crud
from app.database.session import get_db
from app.security import get_current_user_with_access_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user_with_access_token)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    return await user_crud.update_user(db, current_user.id, user_update)


@router.post("/me/verify", response_model=UserOut)
async def verify_me(
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    return await user_crud.verify_user(db, current_user.id)
