"""
API routes for Gig management.
Provides CRUD operations and geospatial search for gigs.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.gig_crud import GigCRUD
from app.database.session import get_db
from app.models import User, GigStatus
from app.schemas.gig_schema import (
    GigCreateSchema, 
    GigUpdateSchema, 
    GigStatusUpdateSchema,
    GigResponseSchema, 
    GigSearchSchema,
    GigListResponseSchema
)
from app.security import get_current_user_with_access_token


router = APIRouter(prefix="/gigs", tags=["gigs"])


def gig_to_response(gig, distance_km: Optional[float] = None) -> GigResponseSchema:
    """Convert Gig model to response schema"""
    return GigResponseSchema(
        id=gig.id,
        title=gig.title,
        description=gig.description,
        duration_hours=gig.duration_hours,
        budget=gig.budget,
        address_text=gig.address_text,
        status=gig.status,
        image_urls=gig.image_urls,
        created_at=gig.created_at,
        updated_at=gig.updated_at,
        starts_at=gig.starts_at,
        completed_at=gig.completed_at,
        seeker_id=gig.seeker_id,
        helper_id=gig.helper_id,
        latitude=None,
        longitude=None,
        distance_km=distance_km
    )


@router.post("/", response_model=GigResponseSchema, status_code=http_status.HTTP_201_CREATED)
async def create_gig(
    gig_data: GigCreateSchema,
    current_user: User = Depends(get_current_user_with_access_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new gig.
    Only authenticated users can create gigs (they become the seeker).
    """
    try:
        gig = await GigCRUD.create_gig(session, gig_data, current_user.id)
        return gig_to_response(gig)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create gig: {str(e)}"
        )


@router.get("/search", response_model=GigListResponseSchema)
async def search_gigs(
    latitude: float = Query(None, ge=-90, le=90, description="Search center latitude"),
    longitude: float = Query(None, ge=-180, le=180, description="Search center longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100, description="Search radius in kilometers"),
    min_budget: float = Query(None, ge=0, description="Minimum budget filter"),
    max_budget: float = Query(None, ge=0, description="Maximum budget filter"),
    max_duration: int = Query(None, ge=1, description="Maximum duration in hours"),
    status: GigStatus = Query(GigStatus.PENDING, description="Gig status filter"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    session: AsyncSession = Depends(get_db)
):
    """
    Search gigs with optional geospatial and other filters.
    If latitude/longitude provided, results are ordered by distance.
    """
    search_params = GigSearchSchema(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        min_budget=min_budget,
        max_budget=max_budget,
        max_duration=max_duration,
        status=status,
        limit=limit,
        offset=offset
    )
    
    try:
        gigs, total_count = await GigCRUD.search_gigs(session, search_params)
        
        gig_responses = [gig_to_response(gig) for gig in gigs]
        
        return GigListResponseSchema(
            gigs=gig_responses,
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=offset + len(gigs) < total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/", response_model=GigListResponseSchema)
async def list_gigs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db)
):
    """
    List all pending gigs (no geospatial filtering).
    Ordered by creation date (newest first).
    """
    search_params = GigSearchSchema(
        latitude=None,
        longitude=None,
        radius_km=10.0,
        min_budget=None,
        max_budget=None,
        max_duration=None,
        status=GigStatus.PENDING,
        limit=limit,
        offset=offset
    )
    
    gigs, total_count = await GigCRUD.search_gigs(session, search_params)
    gig_responses = [gig_to_response(gig) for gig in gigs]
    
    return GigListResponseSchema(
        gigs=gig_responses,
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=offset + len(gigs) < total_count
    )


@router.get("/my-gigs", response_model=GigListResponseSchema)
async def get_my_gigs(
    as_seeker: bool = Query(True, description="Get gigs as seeker (created) vs helper (accepted)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_with_access_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Get current user's gigs.
    as_seeker=True: gigs user created (as seeker)
    as_seeker=False: gigs user accepted (as helper)
    """
    gigs, total_count = await GigCRUD.get_user_gigs(
        session, current_user.id, as_seeker, limit, offset
    )
    
    gig_responses = [gig_to_response(gig) for gig in gigs]
    
    return GigListResponseSchema(
        gigs=gig_responses,
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=offset + len(gigs) < total_count
    )


@router.get("/{gig_id}", response_model=GigResponseSchema)
async def get_gig(
    gig_id: UUID,
    session: AsyncSession = Depends(get_db)
):
    """Get specific gig by ID"""
    gig = await GigCRUD.get_gig_by_id(session, gig_id)
    
    if not gig:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    return gig_to_response(gig)


@router.put("/{gig_id}", response_model=GigResponseSchema)
async def update_gig(
    gig_id: UUID,
    gig_data: GigUpdateSchema,
    current_user: User = Depends(get_current_user_with_access_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Update gig details.
    Only the seeker who created the gig can update it.
    """
    gig = await GigCRUD.update_gig(session, gig_id, gig_data, current_user.id)
    
    if not gig:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Gig not found or you don't have permission to update it"
        )
    
    return gig_to_response(gig)


@router.delete("/{gig_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_gig(
    gig_id: UUID,
    current_user: User = Depends(get_current_user_with_access_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Delete gig.
    Only the seeker who created it can delete it, and only if no helper is assigned.
    """
    success = await GigCRUD.delete_gig(session, gig_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Gig not found, already assigned, or you don't have permission to delete it"
        )


@router.post("/{gig_id}/accept", response_model=GigResponseSchema)
async def accept_gig(
    gig_id: UUID,
    current_user: User = Depends(get_current_user_with_access_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Accept a gig as a helper.
    Changes status from PENDING to ACCEPTED and assigns the current user as helper.
    """
    gig = await GigCRUD.accept_gig(session, gig_id, current_user.id)
    
    if not gig:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Gig not found, already assigned, or not in pending status"
        )
    
    return gig_to_response(gig)


@router.put("/{gig_id}/status", response_model=GigResponseSchema)
async def update_gig_status(
    gig_id: UUID,
    status_data: GigStatusUpdateSchema,
    current_user: User = Depends(get_current_user_with_access_token),
    session: AsyncSession = Depends(get_db)
):
    """
    Update gig status.
    Only seeker or assigned helper can update status.
    """
    gig = await GigCRUD.update_gig_status(
        session, gig_id, status_data.status, current_user.id
    )
    
    if not gig:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Gig not found or you don't have permission to update its status"
        )
    
    return gig_to_response(gig)