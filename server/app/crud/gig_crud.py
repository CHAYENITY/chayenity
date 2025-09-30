"""
CRUD operations for Gig model.
Handles database operations for gig management including geospatial queries.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Sequence
from uuid import UUID

from sqlalchemy import and_, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint, ST_SetSRID

from app.models import Gig, GigStatus, User
from app.schemas.gig_schema import GigCreateSchema, GigUpdateSchema, GigSearchSchema


class GigCRUD:
    """CRUD operations for Gig model"""
    
    @staticmethod
    async def create_gig(
        session: AsyncSession, 
        gig_data: GigCreateSchema, 
        seeker_id: UUID
    ) -> Gig:
        """Create a new gig"""
        # Create location point if coordinates provided
        location = None
        if gig_data.location:
            from geoalchemy2 import WKTElement
            location = WKTElement(
                f"POINT({gig_data.location.longitude} {gig_data.location.latitude})",
                srid=4326
            )
        
        gig = Gig(
            title=gig_data.title,
            description=gig_data.description,
            duration_hours=gig_data.duration_hours,
            budget=gig_data.budget,
            location=location,
            address_text=gig_data.address_text,
            status=GigStatus.PENDING,
            image_urls=gig_data.image_urls or [],
            starts_at=gig_data.starts_at,
            seeker_id=seeker_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(gig)
        await session.commit()
        await session.refresh(gig)
        return gig
    
    @staticmethod
    async def get_gig_by_id(session: AsyncSession, gig_id: UUID) -> Optional[Gig]:
        """Get gig by ID with seeker and helper information"""
        statement = select(Gig).where(Gig.id == gig_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_gig(
        session: AsyncSession, 
        gig_id: UUID, 
        gig_data: GigUpdateSchema,
        user_id: UUID
    ) -> Optional[Gig]:
        """Update gig (only by seeker who created it)"""
        statement = select(Gig).where(
            and_(col(Gig.id) == gig_id, col(Gig.seeker_id) == user_id)
        )
        result = await session.execute(statement)
        gig = result.scalar_one_or_none()
        
        if not gig:
            return None
        
        # Update fields if provided
        update_data = gig_data.dict(exclude_unset=True)
        
        # Handle location update
        if "location" in update_data and update_data["location"]:
            from geoalchemy2 import WKTElement
            location_data = update_data["location"]
            gig.location = WKTElement(
                f"POINT({location_data['longitude']} {location_data['latitude']})",
                srid=4326
            )
            del update_data["location"]
        
        # Update other fields
        for field, value in update_data.items():
            if hasattr(gig, field):
                setattr(gig, field, value)
        
        gig.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(gig)
        return gig
    
    @staticmethod
    async def delete_gig(session: AsyncSession, gig_id: UUID, user_id: UUID) -> bool:
        """Delete gig (only by seeker who created it, and only if not accepted)"""
        statement = select(Gig).where(
            and_(
                col(Gig.id) == gig_id,
                col(Gig.seeker_id) == user_id,
                col(Gig.helper_id).is_(None),  # Can't delete if helper assigned
                col(Gig.status) == GigStatus.PENDING
            )
        )
        result = await session.execute(statement)
        gig = result.scalar_one_or_none()
        
        if not gig:
            return False
        
        await session.delete(gig)
        await session.commit()
        return True
    
    @staticmethod
    async def accept_gig(
        session: AsyncSession, 
        gig_id: UUID, 
        helper_id: UUID
    ) -> Optional[Gig]:
        """Helper accepts a gig"""
        statement = select(Gig).where(
            and_(
                col(Gig.id) == gig_id,
                col(Gig.status) == GigStatus.PENDING,
                col(Gig.helper_id).is_(None)
            )
        )
        result = await session.execute(statement)
        gig = result.scalar_one_or_none()
        
        if not gig:
            return None
        
        gig.helper_id = helper_id
        gig.status = GigStatus.ACCEPTED
        gig.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(gig)
        return gig
    
    @staticmethod
    async def update_gig_status(
        session: AsyncSession, 
        gig_id: UUID, 
        new_status: GigStatus,
        user_id: UUID
    ) -> Optional[Gig]:
        """Update gig status (by seeker or helper involved)"""
        statement = select(Gig).where(
            and_(
                col(Gig.id) == gig_id,
                or_(col(Gig.seeker_id) == user_id, col(Gig.helper_id) == user_id)
            )
        )
        result = await session.execute(statement)
        gig = result.scalar_one_or_none()
        
        if not gig:
            return None
        
        gig.status = new_status
        gig.updated_at = datetime.now(timezone.utc)
        
        # Set completion time if marked as completed
        if new_status == GigStatus.COMPLETED:
            gig.completed_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(gig)
        return gig
    
    @staticmethod
    async def search_gigs(
        session: AsyncSession, 
        search_params: GigSearchSchema,
        user_location: Optional[Tuple[float, float]] = None
    ) -> Tuple[List[Gig], int]:
        """Search gigs with geospatial and other filters"""
        
        # Base query
        query = select(Gig).where(col(Gig.status) == search_params.status)
        count_query = select(func.count(col(Gig.id))).where(col(Gig.status) == search_params.status)
        
        # Geospatial filter - search around specified location
        if search_params.latitude and search_params.longitude:
            # Create search point with correct SRID (4326 for WGS84/GPS coordinates)
            search_point = ST_SetSRID(
                ST_MakePoint(search_params.longitude, search_params.latitude),
                4326
            )
            
            # Filter by distance
            distance_filter = ST_DWithin(
                col(Gig.location),
                search_point,
                (search_params.radius_km or 10.0) * 1000  # Convert km to meters
            )
            
            query = query.where(distance_filter)
            count_query = count_query.where(distance_filter)
            
            # Add distance calculation for sorting
            query = query.add_columns(
                ST_Distance(col(Gig.location), search_point).label('distance')
            ).order_by(text('distance'))
        
        # Budget filters
        if search_params.min_budget is not None:
            budget_filter = col(Gig.budget) >= search_params.min_budget
            query = query.where(budget_filter)
            count_query = count_query.where(budget_filter)
            
        if search_params.max_budget is not None:
            budget_filter = col(Gig.budget) <= search_params.max_budget
            query = query.where(budget_filter)
            count_query = count_query.where(budget_filter)
        
        # Duration filter
        if search_params.max_duration is not None:
            duration_filter = col(Gig.duration_hours) <= search_params.max_duration
            query = query.where(duration_filter)
            count_query = count_query.where(duration_filter)
        
        # Add default ordering if no geospatial search
        if not (search_params.latitude and search_params.longitude):
            query = query.order_by(col(Gig.created_at).desc())
        
        # Pagination
        query = query.offset(search_params.offset).limit(search_params.limit)
        
        # Execute queries
        result = await session.execute(query)
        count_result = await session.execute(count_query)
        
        # Handle results based on whether we have distance calculation
        if search_params.latitude and search_params.longitude:
            # Results include distance column
            rows = result.all()
            gigs = [row[0] for row in rows]  # Extract gig objects
            # TODO: Add distance to gig objects for response
        else:
            gigs = result.scalars().all()
        
        total_count = count_result.scalar() or 0
        
        return list(gigs), total_count
    
    @staticmethod
    async def get_user_gigs(
        session: AsyncSession, 
        user_id: UUID, 
        as_seeker: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Gig], int]:
        """Get gigs created by user (as seeker) or accepted by user (as helper)"""
        
        if as_seeker:
            query = select(Gig).where(col(Gig.seeker_id) == user_id)
            count_query = select(func.count(col(Gig.id))).where(col(Gig.seeker_id) == user_id)
        else:
            query = select(Gig).where(col(Gig.helper_id) == user_id)
            count_query = select(func.count(col(Gig.id))).where(col(Gig.helper_id) == user_id)
        
        # Order by most recent
        query = query.order_by(col(Gig.created_at).desc()).offset(offset).limit(limit)
        
        result = await session.execute(query)
        count_result = await session.execute(count_query)
        
        gigs = result.scalars().all()
        total_count = count_result.scalar() or 0
        
        return list(gigs), total_count