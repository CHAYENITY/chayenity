# schemas/user_schema.py
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.modules.users.address_schema import AddressBase
from app.modules.users.user_validation import (
    validate_email as user_validate_email,
    validate_password as user_validate_password,
    validate_phone_number as user_validate_phone_number,
    validate_first_name as user_validate_first_name,
    validate_last_name as user_validate_last_name,
    validate_address as user_validate_address,
)

# TODO: UPLOAD PROFILE IMAGE


class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    additional_contact: Optional[str] = None
    address: AddressBase


class UserCreate(UserBase):
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return user_validate_email(v)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        return user_validate_phone_number(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return user_validate_password(v)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        return user_validate_first_name(v)

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        return user_validate_last_name(v)

    @field_validator("address")
    @classmethod
    def validate_address(cls, v):
        return user_validate_address(v)


class UserUpdate(UserBase):
    pass


class UserOut(UserBase):
    profile_image_url: Optional[str] = None

    is_available: bool
    is_verified: bool
    reputation_score: float
    total_reviews: int

    created_at: datetime
    updated_at: datetime
    id: UUID

    model_config = ConfigDict(from_attributes=True)
