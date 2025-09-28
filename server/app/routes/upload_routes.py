"""
File upload and image management routes for Hourz Backend.
Handles profile images, gig images, and file serving.
"""

from typing import List, Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.security import get_current_user_with_access_token as get_current_user
from app.models import User, UploadedFile
from app.crud.upload_crud import upload_crud
from app.schemas.upload_schemas import (
    FileUploadResponse, 
    FileMetadata, 
    ProfileImageUpdate,
    GigImageUpdate
)


router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/profile", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_profile_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a profile image for the current user."""
    
    # Save file
    uploaded_file = await upload_crud.save_file(
        session=db,
        file=file,
        user_id=current_user.id,
        category="profile"
    )
    
    # Generate URL
    file_url = upload_crud.get_file_url(uploaded_file, "http://localhost:8000")
    
    return FileUploadResponse(
        file_id=uploaded_file.id,
        filename=uploaded_file.filename,
        original_filename=uploaded_file.original_filename,
        file_size=uploaded_file.file_size,
        content_type=uploaded_file.content_type,
        url=file_url,
        uploaded_at=uploaded_file.uploaded_at
    )


@router.post("/gig", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_gig_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload an image for a gig."""
    
    # Save file
    uploaded_file = await upload_crud.save_file(
        session=db,
        file=file,
        user_id=current_user.id,
        category="gig"
    )
    
    # Generate URL
    file_url = upload_crud.get_file_url(uploaded_file, "http://localhost:8000")
    
    return FileUploadResponse(
        file_id=uploaded_file.id,
        filename=uploaded_file.filename,
        original_filename=uploaded_file.original_filename,
        file_size=uploaded_file.file_size,
        content_type=uploaded_file.content_type,
        url=file_url,
        uploaded_at=uploaded_file.uploaded_at
    )


@router.get("/{file_id}")
async def serve_uploaded_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Serve an uploaded file by its ID."""
    
    # Get file record
    file_record = await upload_crud.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if physical file exists
    file_path = upload_crud.get_file_path(file_record)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    # Serve file
    return FileResponse(
        path=file_path,
        media_type=file_record.content_type,
        filename=file_record.original_filename
    )


@router.get("/my-files/", response_model=List[FileMetadata])
async def get_my_uploaded_files(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get files uploaded by the current user."""
    
    files = await upload_crud.get_user_files(
        session=db,
        user_id=current_user.id,
        category=category,
        limit=limit,
        offset=offset
    )
    
    return [
        FileMetadata(
            file_id=f.id,
            filename=f.filename,
            original_filename=f.original_filename,
            file_size=f.file_size,
            content_type=f.content_type,
            upload_category=f.upload_category,
            uploaded_by=f.uploaded_by,
            uploaded_at=f.uploaded_at,
            is_active=f.is_active
        )
        for f in files
    ]


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploaded_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an uploaded file."""
    
    success = await upload_crud.delete_file(
        session=db,
        file_id=file_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or not owned by you"
        )


# Integration endpoints for updating profile/gig images

@router.put("/profile/set", status_code=status.HTTP_200_OK)
async def set_profile_image(
    update_data: ProfileImageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set user's profile image URL."""
    from app.crud import user_crud
    
    # Update user's profile image URL
    current_user.profile_image_url = update_data.profile_image_url
    db.add(current_user)
    await db.commit()
    
    return {"message": "Profile image updated successfully"}


@router.get("/gig-images/{gig_id}")
async def get_gig_images(
    gig_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all images associated with a gig."""
    from app.crud.gig_crud import GigCRUD
    
    # Get gig and verify ownership or visibility
    gig = await GigCRUD.get_gig_by_id(db, gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    return {
        "gig_id": gig_id,
        "image_urls": gig.image_urls or []
    }