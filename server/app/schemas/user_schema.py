# schemas/user_schema.py
import re
from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(SQLModel):
    email: EmailStr
    first_name: Optional[str] = None  # ชื่อ - Optional for two-step registration
    last_name: Optional[str] = None  # นามสกุล - Optional for two-step registration
    bio: Optional[str] = None  # แนะนำตัวเอง
    phone_number: Optional[str] = None  # เบอร์โทรศัพท์ - Optional for two-step registration
    additional_contact: Optional[str] = None  # ช่องทางติดต่อเพิ่มเติม (LINE ID, etc.)
    is_profile_setup: bool = False  # Track if profile setup is complete


class UserCreate(SQLModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserProfileSetup(SQLModel):
    first_name: str
    last_name: str
    bio: Optional[str] = None
    phone_number: str
    additional_contact: Optional[str] = None
    profile_image_url: Optional[str] = None
    address: Optional["AddressCreate"] = None

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError("First name is required")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError("Last name is required")
        return v.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not v:
            raise ValueError("Phone number is required")
        # Allow Thai phone numbers and international format
        if re.fullmatch(r"(\+66|0)[0-9]{8,9}", v) or re.fullmatch(r"\+[0-9]{10,15}", v):
            return v.strip()
        raise ValueError(
            "Phone number must be a valid Thai number (+66xxxxxxxxx or 0xxxxxxxxx) or international format"
        )


# === ADDRESS SCHEMAS ===
class AddressBase(SQLModel):
    address_text: str
    district: str  # อำเภอ/เขต
    province: str  # จังหวัด
    postal_code: Optional[str] = None
    country: str = "Thailand"


class AddressCreate(AddressBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AddressRead(AddressBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: UUID


<<<<<<< HEAD
# Base schema with common fields (excluding sensitive fields)
class UserBase(SQLModel):
    email: EmailStr
    first_name: Optional[str] = None  # ชื่อ - Optional for two-step registration
    last_name: Optional[str] = None   # นามสกุล - Optional for two-step registration
    bio: Optional[str] = None  # แนะนำตัวเอง
    phone_number: Optional[str] = None  # เบอร์โทรศัพท์ - Optional for two-step registration
    additional_contact: Optional[str] = None  # ช่องทางติดต่อเพิ่มเติม (LINE ID, etc.)
    is_profile_complete: bool = False  # Track if profile setup is complete


# Schema for creating users (includes password and address)
class UserCreate(UserBase):
    password: str
    address: Optional[AddressCreate] = None  # ตำแหน่งปัจจุบัน

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # Allow Thai phone numbers and international format
        if re.fullmatch(r"(\+66|0)[0-9]{8,9}", v) or re.fullmatch(r"\+[0-9]{10,15}", v):
            return v.strip()
        raise ValueError(
            "Phone number must be a valid Thai number (+66xxxxxxxxx or 0xxxxxxxxx) or international format"
        )

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if len(v.strip()) < 1:
            raise ValueError("First name cannot be empty")
        return v.strip()

    @field_validator("last_name") 
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if len(v.strip()) < 1:
            raise ValueError("Last name cannot be empty")
        return v.strip()


=======
>>>>>>> 9fff0e8f0a89a3848658d096c2637bc1989b6fd8
# Schema for returning user data (excludes sensitive fields)
class UserOut(UserBase):
    id: UUID
    profile_image_url: Optional[str] = None
    is_verified: bool
    reputation_score: float
    created_at: datetime
    addresses: List[AddressRead] = []

    # Computed properties
    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.first_name:
            return self.first_name.strip()
        elif self.last_name:
            return self.last_name.strip()
        else:
            return ""

    @property
    def current_address(self) -> Optional[AddressRead]:
        if self.addresses:
            return max(self.addresses, key=lambda addr: addr.updated_at)
        return None


# Schema for updating user profile
class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    additional_contact: Optional[str] = None
    profile_image_url: Optional[str] = None
    address: Optional[AddressCreate] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if re.fullmatch(r"(\+66|0)[0-9]{8,9}", v) or re.fullmatch(r"\+[0-9]{10,15}", v):
            return v.strip()
        raise ValueError(
            "Phone number must be a valid Thai number (+66xxxxxxxxx or 0xxxxxxxxx) or international format"
        )

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 1:
            raise ValueError("First name must be at least 1 character long")
        return v.strip() if v else v

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 1:
            raise ValueError("Last name must be at least 1 character long")
        return v.strip() if v else v


# Schema for updating user location (now creates a new address)
class LocationUpdate(SQLModel):
    address_text: str
    district: str
    province: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not -180 <= v <= 180:
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
