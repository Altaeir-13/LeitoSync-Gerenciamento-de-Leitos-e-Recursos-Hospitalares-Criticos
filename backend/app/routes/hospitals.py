from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.models.hospital import Hospital
from app.schemas.base import HospitalResponse

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

@router.get("", response_model=List[HospitalResponse])
async def list_hospitals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hospital))
    return result.scalars().all()
