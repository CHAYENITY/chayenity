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


# Schema for updating user location
class LocationUpdate(SQLModel):
    latitude: float
    longitude: float
    address_text: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


# Schema for updating availability status
class AvailabilityUpdate(SQLModel):
    is_available: bool


# Schema for nearby users search
class NearbyUsersRequest(SQLModel):
    latitude: float
    longitude: float
    radius: float = 5.0  # Default 5km radius
    only_available: bool = True  # Only show available helpers

    @field_validator("radius")
    @classmethod
    def validate_radius(cls, v: float) -> float:
        if not 0.1 <= v <= 50.0:
            raise ValueError("Radius must be between 0.1 and 50 kilometers")
        return v


# Schema for nearby user response
class NearbyUserOut(SQLModel):
    id: UUID
    full_name: str
    profile_image_url: Optional[str] = None
    reputation_score: float
    total_reviews: int
    is_available: bool
    distance_km: float  # Distance from search point
    address_text: Optional[str] = None


# Enhanced profile schema with location and availability
class UserProfileOut(UserOut):
    is_available: bool
    total_reviews: int
    address_text: Optional[str] = None
    has_location: bool = False  # Indicates if user has set a fixed location
