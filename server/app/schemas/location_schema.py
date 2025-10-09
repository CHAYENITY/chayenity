# schemas/location_schema.py
from pydantic import field_validator, BaseModel
from typing import Optional
from uuid import UUID


# Schema for updating user location (now creates a new address)
class LocationUpdate(BaseModel):
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
class AvailabilityUpdate(BaseModel):
    is_available: bool


# Schema for nearby users search
class NearbyUsersRequest(BaseModel):
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
class NearbyUserOut(BaseModel):
    id: UUID
    full_name: str
    profile_image_url: Optional[str] = None
    reputation_score: float
    total_reviews: int
    is_available: bool
    distance_km: float  # Distance from search point
    address_text: Optional[str] = None
