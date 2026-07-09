from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.concurrency_event import ConcurrencyEvent
from app.schemas.base import AuditLogResponse, ConcurrencyEventResponse

router = APIRouter(tags=["logs"])

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
    return result.scalars().all()

@router.get("/concurrency/events", response_model=List[ConcurrencyEventResponse])
async def list_concurrency_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ConcurrencyEvent).order_by(ConcurrencyEvent.created_at.desc()))
    return result.scalars().all()
