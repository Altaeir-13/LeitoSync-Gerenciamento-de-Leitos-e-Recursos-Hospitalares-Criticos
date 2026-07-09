from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.models.hospital import Hospital
from app.models.resource import Resource
from app.core.enums import ResourceStatus
from app.schemas.base import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(db: AsyncSession = Depends(get_db)):
    hospitals_count = await db.scalar(select(func.count()).select_from(Hospital))
    resources_count = await db.scalar(select(func.count()).select_from(Resource))
    
    result = await db.execute(
        select(Resource.status, func.count(Resource.id))
        .group_by(Resource.status)
    )
    status_counts = dict(result.all())
    
    available = status_counts.get(ResourceStatus.AVAILABLE, 0)
    reserved = status_counts.get(ResourceStatus.RESERVED, 0)
    occupied = status_counts.get(ResourceStatus.OCCUPIED, 0)
    blocked = status_counts.get(ResourceStatus.BLOCKED, 0)
    maintenance = status_counts.get(ResourceStatus.MAINTENANCE, 0)
    
    occupancy_rate = 0.0
    if resources_count > 0:
        occupancy_rate = (occupied + reserved) / resources_count * 100

    return DashboardSummaryResponse(
        total_hospitals=hospitals_count or 0,
        total_resources=resources_count or 0,
        available=available,
        reserved=reserved,
        occupied=occupied,
        blocked=blocked,
        maintenance=maintenance,
        occupancy_rate=occupancy_rate
    )
