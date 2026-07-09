from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.base import ResourceResponse, ResourceDetailResponse, ReservationCreate, ActionRequest
from app.repositories.resource_repo import ResourceRepository
from app.core.enums import ResourceStatus
from app.core.exceptions import ConcurrencyConflictException, ResourceNotFoundException
from app.routes.ws import manager

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("", response_model=List[ResourceResponse])
async def list_resources(db: AsyncSession = Depends(get_db)):
    resources = await ResourceRepository.get_all(db)
    return resources

@router.get("/availability", response_model=List[ResourceResponse])
async def check_availability(db: AsyncSession = Depends(get_db)):
    resources = await ResourceRepository.get_all(db)
    return [r for r in resources if r.status == ResourceStatus.AVAILABLE]

@router.get("/{resource_id}", response_model=ResourceDetailResponse)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    return await ResourceRepository.get_by_id(db, resource_id)

@router.post("/{resource_id}/reserve", response_model=ResourceResponse)
async def reserve_resource(resource_id: int, req: ReservationCreate, db: AsyncSession = Depends(get_db)):
    try:
        resource = await ResourceRepository.reserve(db, resource_id, req)
        await db.commit()
        await db.refresh(resource)
        # Emit websocket event
        await manager.broadcast_resource_update(resource.id, resource.status.value)
        return resource
    except ConcurrencyConflictException as e:
        await db.rollback()
        raise e
    except ResourceNotFoundException as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def _change_status(resource_id: int, new_status: ResourceStatus, req: ActionRequest, db: AsyncSession):
    try:
        resource = await ResourceRepository.change_status(db, resource_id, new_status, req)
        await db.commit()
        await db.refresh(resource)
        await manager.broadcast_resource_update(resource.id, resource.status.value)
        return resource
    except (ConcurrencyConflictException, ResourceNotFoundException) as e:
        await db.rollback()
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{resource_id}/release", response_model=ResourceResponse)
async def release_resource(resource_id: int, req: ActionRequest, db: AsyncSession = Depends(get_db)):
    return await _change_status(resource_id, ResourceStatus.AVAILABLE, req, db)

@router.post("/{resource_id}/occupy", response_model=ResourceResponse)
async def occupy_resource(resource_id: int, req: ActionRequest, db: AsyncSession = Depends(get_db)):
    return await _change_status(resource_id, ResourceStatus.OCCUPIED, req, db)

@router.post("/{resource_id}/block", response_model=ResourceResponse)
async def block_resource(resource_id: int, req: ActionRequest, db: AsyncSession = Depends(get_db)):
    return await _change_status(resource_id, ResourceStatus.BLOCKED, req, db)

@router.post("/{resource_id}/maintenance", response_model=ResourceResponse)
async def maintenance_resource(resource_id: int, req: ActionRequest, db: AsyncSession = Depends(get_db)):
    return await _change_status(resource_id, ResourceStatus.MAINTENANCE, req, db)
