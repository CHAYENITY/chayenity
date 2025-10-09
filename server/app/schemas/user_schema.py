# schemas/user_schema.py
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.address_schema import AddressBase
from app.validations.user_validation import (
    validate_email as user_validate_email,
    validate_password as user_validate_password,
    validate_phone_number as user_validate_phone_number,
    validate_first_name as user_validate_first_name,
    validate_last_name as user_validate_last_name,
)

# TODO: UPLOAD PROFILE IMAGE


class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    additional_contact: Optional[str] = None
    address: Optional[AddressBase] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return user_validate_email(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return user_validate_password(v)


class UserProfileUpsert(UserBase):
    pass

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        return user_validate_phone_number(v)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        return user_validate_first_name(v)

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        return user_validate_last_name(v)


class UserOut(UserBase):
    email: EmailStr
    profile_image_url: Optional[str] = None

    is_profile_setup: bool
    is_available: bool
    is_verified: bool
    reputation_score: float
    total_reviews: int

    created_at: datetime
    updated_at: datetime
    id: UUID

    model_config = ConfigDict(from_attributes=True)
