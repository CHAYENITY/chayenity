# schemas/user_schema.py
import re
from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# Base schema with common fields (excluding sensitive fields)
class UserBase(SQLModel):
    email: EmailStr = "user.name@example.com"
    full_name: str = "John Doe"
    contact_info: Optional[str] = None  # phone or LINE ID
    address_text: Optional[str] = None


# Schema for creating users (includes password)
class UserCreate(UserBase):
    password: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v

    @field_validator("contact_info")
    @classmethod
    def validate_contact_info(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # Allow phone numbers or LINE IDs
        if re.fullmatch(r"[0-9]{7,15}", v) or re.fullmatch(r"[a-zA-Z0-9._-]{3,30}", v):
            return v.strip()
        raise ValueError(
            "Contact info must be a valid phone number (7-15 digits) or LINE ID (3-30 characters)"
        )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        return v.strip()


# Schema for returning user data (excludes sensitive fields)
class UserOut(UserBase):
    id: UUID
    profile_image_url: Optional[str] = None
    is_verified: bool
    reputation_score: float
    created_at: datetime


# Schema for updating user profile
class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    contact_info: Optional[str] = None
    address_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    profile_image_url: Optional[str] = None

    @field_validator("contact_info")
    @classmethod
    def validate_contact_info(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if re.fullmatch(r"[0-9]{7,15}", v) or re.fullmatch(r"[a-zA-Z0-9._-]{3,30}", v):
            return v.strip()
        raise ValueError(
            "Contact info must be a valid phone number (7-15 digits) or LINE ID (3-30 characters)"
        )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        return v.strip() if v else v
