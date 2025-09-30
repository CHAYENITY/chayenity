"""
CRUD operations for file upload and image management.
Handles file storage, metadata tracking, and file serving.
"""

import os
import uuid
import shutil
from typing import Optional, List, BinaryIO
from pathlib import Path
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from fastapi import UploadFile, HTTPException, status

from app.models import UploadedFile, User
from app.schemas.upload_schemas import ImageValidationConfig


class UploadCRUD:
    """CRUD operations for file upload management"""
    
    def __init__(self, upload_dir: str = "uploads"):
        """Initialize with upload directory."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for category in ["profile", "gig"]:
            (self.upload_dir / category).mkdir(exist_ok=True)
    
    async def save_file(
        self, 
        session: AsyncSession, 
        file: UploadFile, 
        user_id: UUID,
        category: str = "profile"
    ) -> UploadedFile:
        """Save uploaded file to disk and database."""
        
        # Validate file
        self._validate_file(file, category)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / category / unique_filename
        
        # Save file to disk
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        finally:
            await file.close()
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Create database record
        uploaded_file = UploadedFile(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=str(file_path),
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            upload_category=category,
            uploaded_by=user_id
        )
        
        session.add(uploaded_file)
        await session.commit()
        await session.refresh(uploaded_file)
        
        return uploaded_file
    
    async def get_file_by_id(
        self, session: AsyncSession, file_id: UUID
    ) -> Optional[UploadedFile]:
        """Get file record by ID."""
        stmt = select(UploadedFile).where(
            col(UploadedFile.id) == file_id,
            col(UploadedFile.is_active) == True
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_files(
        self, 
        session: AsyncSession, 
        user_id: UUID, 
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[UploadedFile]:
        """Get files uploaded by user."""
        stmt = select(UploadedFile).where(
            col(UploadedFile.uploaded_by) == user_id,
            col(UploadedFile.is_active) == True
        )
        
        if category:
            stmt = stmt.where(col(UploadedFile.upload_category) == category)
        
        stmt = stmt.order_by(col(UploadedFile.uploaded_at).desc())
        stmt = stmt.offset(offset).limit(limit)
        
        result = await session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_file(
        self, session: AsyncSession, file_id: UUID, user_id: UUID
    ) -> bool:
        """Soft delete a file (mark as inactive)."""
        stmt = select(UploadedFile).where(
            col(UploadedFile.id) == file_id,
            col(UploadedFile.uploaded_by) == user_id,
            col(UploadedFile.is_active) == True
        )
        result = await session.execute(stmt)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return False
        
        # Soft delete - mark as inactive
        file_record.is_active = False
        await session.commit()
        
        # Optionally, delete physical file
        try:
            file_path = Path(file_record.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception:
            # Log error but don't fail the operation
            pass
        
        return True
    
    def get_file_path(self, uploaded_file: UploadedFile) -> Path:
        """Get the physical file path."""
        return Path(uploaded_file.file_path)
    
    def get_file_url(self, uploaded_file: UploadedFile, base_url: str) -> str:
        """Generate public URL for the file."""
        return f"{base_url}/api/upload/{uploaded_file.id}"
    
    def _validate_file(self, file: UploadFile, category: str) -> None:
        """Validate uploaded file."""
        config = ImageValidationConfig()
        
        # Check file size
        if file.size and file.size > config.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {config.max_file_size} bytes"
            )
        
        # Check content type
        if file.content_type not in config.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type. Allowed: {', '.join(config.allowed_types)}"
            )
        
        # Check filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )


# Global instance
upload_crud = UploadCRUD()