from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.models.resource_type import ResourceType
from app.schemas.base import ResourceTypeResponse

router = APIRouter(prefix="/resource-types", tags=["resource-types"])

@router.get("", response_model=List[ResourceTypeResponse])
async def list_resource_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResourceType))
    return result.scalars().all()
