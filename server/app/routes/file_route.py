from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from app.models import User, UploadedFile
from app.database.session import get_db
from app.security import get_current_user_with_access_token

router = APIRouter(prefix="/files", tags=["File Management"])

# Configure upload directories - Use relative path for development, absolute for production
import os
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))  # Configurable path
PROFILE_DIR = UPLOAD_DIR / "profile"
GIG_DIR = UPLOAD_DIR / "gig"
GENERAL_DIR = UPLOAD_DIR / "general"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, PROFILE_DIR, GIG_DIR, GENERAL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload/{category}")
async def upload_file(
    category: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload files to server storage
    Categories: 'profile', 'gig', 'general'
    """
    # Validate category
    if category not in ["profile", "gig", "general"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size: 5MB")
    
    # Generate unique filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Determine upload directory
    if category == "profile":
        upload_path = PROFILE_DIR / unique_filename
    elif category == "gig":
        upload_path = GIG_DIR / unique_filename
    else:
        upload_path = GENERAL_DIR / unique_filename
    
    # Save file
    try:
        with open(upload_path, "wb") as buffer:
            buffer.write(content)
        
        # Save file metadata to database
        uploaded_file = UploadedFile(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=str(upload_path),
            file_size=len(content),
            content_type=file.content_type or "application/octet-stream",
            upload_category=category,
            uploaded_by=current_user.id
        )
        
        db.add(uploaded_file)
        await db.commit()
        await db.refresh(uploaded_file)
        
        # Return file URL for frontend
        file_url = f"/api/files/serve/{category}/{unique_filename}"
        
        return {
            "file_id": uploaded_file.id,
            "filename": unique_filename,
            "original_filename": file.filename or "unknown",
            "file_url": file_url,
            "file_size": len(content),
            "category": category
        }
        
    except Exception as e:
        # Clean up file if database save fails
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.get("/serve/{category}/{filename}")
async def serve_file(category: str, filename: str):
    """
    Serve uploaded files to frontend
    Public endpoint - no authentication required for serving
    """
    # Validate category
    if category not in ["profile", "gig", "general"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Construct file path
    if category == "profile":
        file_path = PROFILE_DIR / filename
    elif category == "gig":
        file_path = GIG_DIR / filename
    else:
        file_path = GENERAL_DIR / filename
    
    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Serve file
    return FileResponse(
        path=str(file_path),
        filename=filename,
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Access-Control-Allow-Origin": "*"  # Allow CORS for images
        }
    )


@router.get("/list/{category}")
async def list_user_files(
    category: str,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db)
):
    """List all files uploaded by current user in specific category"""
    from sqlmodel import select
    
    stmt = select(UploadedFile).where(
        UploadedFile.uploaded_by == current_user.id,
        UploadedFile.upload_category == category,
        UploadedFile.is_active == True
    )
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    return [
        {
            "file_id": file.id,
            "filename": file.filename,
            "original_filename": file.original_filename,
            "file_url": f"/api/files/serve/{category}/{file.filename}",
            "file_size": file.file_size,
            "uploaded_at": file.uploaded_at
        }
        for file in files
    ]


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file (soft delete - mark as inactive)"""
    from sqlmodel import select
    
    stmt = select(UploadedFile).where(
        UploadedFile.id == file_id,
        UploadedFile.uploaded_by == current_user.id
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Soft delete - mark as inactive
    file_record.is_active = False
    await db.commit()
    
    # Optionally, delete physical file
    file_path = Path(file_record.file_path)
    if file_path.exists():
        file_path.unlink()
    
    return {"message": "File deleted successfully"}


@router.put("/profile-image")
async def update_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db)
):
    """Upload and set profile image for current user"""
    
    # Validate category
    category = "profile"
    if category not in ["profile", "gig", "general"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size: 5MB")
    
    # Generate unique filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Determine upload directory
    upload_path = PROFILE_DIR / unique_filename
    
    # Save file
    try:
        with open(upload_path, "wb") as buffer:
            buffer.write(content)
        
        # Save file metadata to database
        uploaded_file = UploadedFile(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=str(upload_path),
            file_size=len(content),
            content_type=file.content_type or "application/octet-stream",
            upload_category=category,
            uploaded_by=current_user.id
        )
        
        db.add(uploaded_file)
        
        # Update user's profile_image_url
        file_url = f"/api/files/serve/{category}/{unique_filename}"
        current_user.profile_image_url = file_url
        
        await db.commit()
        await db.refresh(current_user)
        await db.refresh(uploaded_file)
        
        return {
            "message": "Profile image updated successfully",
            "profile_image_url": current_user.profile_image_url,
            "file_details": {
                "file_id": uploaded_file.id,
                "filename": unique_filename,
                "original_filename": file.filename or "unknown",
                "file_url": file_url,
                "file_size": len(content),
                "category": category
            }
        }
        
    except Exception as e:
        # Clean up file if database save fails
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")