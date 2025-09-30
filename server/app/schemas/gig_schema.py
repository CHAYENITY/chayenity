"""
Pydantic schemas for Gig-related operations.
These schemas define the structure for API requests and responses.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from geoalchemy2 import Geometry

from app.models import GigStatus


class GigLocationSchema(BaseModel):
    """Schema for location coordinates"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class GigCreateSchema(BaseModel):
    """Schema for creating a new gig"""
    title: str = Field(..., min_length=3, max_length=200, description="Gig title")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed description")
    duration_hours: int = Field(..., ge=1, le=24, description="Expected duration in hours")
    budget: float = Field(..., ge=0, description="Budget in USD")
    location: Optional[GigLocationSchema] = Field(None, description="Gig location coordinates")
    address_text: str = Field(..., min_length=5, max_length=500, description="Human-readable address")
    image_urls: Optional[List[str]] = Field(default_factory=list, description="List of image URLs")
    starts_at: Optional[datetime] = Field(None, description="Preferred start time")


class GigUpdateSchema(BaseModel):
    """Schema for updating an existing gig"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    duration_hours: Optional[int] = Field(None, ge=1, le=24)
    budget: Optional[float] = Field(None, ge=0)
    location: Optional[GigLocationSchema] = None
    address_text: Optional[str] = Field(None, min_length=5, max_length=500)
    image_urls: Optional[List[str]] = None
    starts_at: Optional[datetime] = None


class GigStatusUpdateSchema(BaseModel):
    """Schema for updating gig status"""
    status: GigStatus = Field(..., description="New gig status")


class GigResponseSchema(BaseModel):
    """Schema for gig responses"""
    id: UUID
    title: str
    description: str
    duration_hours: int
    budget: float
    address_text: str
    status: GigStatus
    image_urls: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    starts_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    seeker_id: UUID
    helper_id: Optional[UUID] = None
    
    # Location data (we'll handle PostGIS separately)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Computed fields
    distance_km: Optional[float] = Field(None, description="Distance from user in kilometers")

    model_config = ConfigDict(from_attributes=True)


class GigSearchSchema(BaseModel):
    """Schema for gig search parameters"""
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Search center latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Search center longitude") 
    radius_km: Optional[float] = Field(10.0, ge=0.1, le=100, description="Search radius in kilometers")
    min_budget: Optional[float] = Field(None, ge=0, description="Minimum budget filter")
    max_budget: Optional[float] = Field(None, ge=0, description="Maximum budget filter")
    max_duration: Optional[int] = Field(None, ge=1, description="Maximum duration filter in hours")
    status: Optional[GigStatus] = Field(GigStatus.PENDING, description="Gig status filter")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Results offset for pagination")


class GigListResponseSchema(BaseModel):
    """Schema for paginated gig list response"""
    gigs: List[GigResponseSchema]
    total_count: int
    limit: int
    offset: int
    has_more: bool