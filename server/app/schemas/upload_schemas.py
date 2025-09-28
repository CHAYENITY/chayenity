"""
File upload and image management schemas for Hourz Backend.
Handles profile images, gig images, and file metadata.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response schema for successful file uploads."""
    file_id: UUID
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    url: str
    uploaded_at: datetime


class ImageUploadRequest(BaseModel):
    """Request schema for image upload metadata."""
    description: Optional[str] = Field(None, max_length=200, description="Optional image description")
    category: str = Field(..., description="Image category: 'profile' or 'gig'")


class ProfileImageUpdate(BaseModel):
    """Schema for updating user profile image."""
    profile_image_url: str = Field(..., description="URL of the uploaded profile image")


class GigImageUpdate(BaseModel):
    """Schema for updating gig images."""
    image_urls: List[str] = Field(..., description="List of image URLs for the gig")


class FileMetadata(BaseModel):
    """File metadata response."""
    file_id: UUID
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    upload_category: str
    uploaded_by: UUID
    uploaded_at: datetime
    is_active: bool = True


class ImageValidationConfig(BaseModel):
    """Configuration for image validation."""
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    max_images_per_gig: int = 5