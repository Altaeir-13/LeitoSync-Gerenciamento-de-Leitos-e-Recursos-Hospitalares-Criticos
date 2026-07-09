from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
import asyncio
from app.database import get_db, async_session_maker
from app.models.concurrency_event import ConcurrencyEvent
from app.schemas.base import ReservationCreate
from app.repositories.resource_repo import ResourceRepository
from app.core.enums import ReservationPriority
from app.core.exceptions import ConcurrencyConflictException

router = APIRouter(prefix="/simulation", tags=["simulation"])

async def simulate_reader(resource_id: int) -> dict:
    async with async_session_maker() as session:
        try:
            resource = await ResourceRepository.get_by_id(session, resource_id)
            return {"success": True, "message": f"Leitura com sucesso. Status: {resource.status.value}", "type": "read"}
        except Exception as e:
            return {"success": False, "message": str(e), "type": "read"}

async def simulate_writer(resource_id: int, writer_id: int) -> dict:
    async with async_session_maker() as session:
        try:
            req = ReservationCreate(
                requester_name=f"Escritor Simulado {writer_id}",
                priority=ReservationPriority.MEDIUM,
                reason="Simulação"
            )
            resource = await ResourceRepository.reserve(session, resource_id, req)
            await session.commit()
            
            # Log event
            event = ConcurrencyEvent(
                resource_id=resource_id,
                operation_type="WRITE",
                success=True,
                message="Reserva confirmada com sucesso."
            )
            session.add(event)
            await session.commit()
            
            return {"success": True, "message": "Reserva confirmada com sucesso", "type": "write"}
        except ConcurrencyConflictException as e:
            await session.rollback()
            event = ConcurrencyEvent(
                resource_id=resource_id,
                operation_type="WRITE",
                success=False,
                message=str(e.detail)
            )
            session.add(event)
            await session.commit()
            return {"success": False, "message": str(e.detail), "type": "write"}
        except Exception as e:
            await session.rollback()
            return {"success": False, "message": str(e), "type": "write"}

@router.post("/readers")
async def run_readers(resource_id: int, count: int = 10):
    tasks = [simulate_reader(resource_id) for _ in range(count)]
    results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if r["success"])
    return {
        "total": count,
        "success": success,
        "failed": count - success,
        "results": results
    }

@router.post("/writers")
async def run_writers(resource_id: int, count: int = 5):
    # Release the resource first if it's already reserved/occupied to allow simulation
    async with async_session_maker() as session:
        try:
            from app.schemas.base import ActionRequest
            from app.core.enums import ResourceStatus
            await ResourceRepository.change_status(
                session, resource_id, ResourceStatus.AVAILABLE, 
                ActionRequest(actor_name="Sistema", reason="Reset da Simulação")
            )
            await session.commit()
        except Exception:
            await session.rollback()
            pass

    tasks = [simulate_writer(resource_id, i) for i in range(count)]
    results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if r["success"])
    return {
        "total": count,
        "success": success,
        "conflicts": count - success,
        "results": results
    }

@router.post("/readers-writers")
async def run_readers_writers(resource_id: int, readers_count: int = 10, writers_count: int = 5):
    # Reset resource
    async with async_session_maker() as session:
        try:
            from app.schemas.base import ActionRequest
            from app.core.enums import ResourceStatus
            await ResourceRepository.change_status(
                session, resource_id, ResourceStatus.AVAILABLE, 
                ActionRequest(actor_name="Sistema", reason="Reset da Simulação")
            )
            await session.commit()
        except Exception:
            await session.rollback()
            pass

    reader_tasks = [simulate_reader(resource_id) for _ in range(readers_count)]
    writer_tasks = [simulate_writer(resource_id, i) for i in range(writers_count)]
    
    # Run all together
    all_tasks = reader_tasks + writer_tasks
    results = await asyncio.gather(*all_tasks)
    
    read_results = [r for r in results if r["type"] == "read"]
    write_results = [r for r in results if r["type"] == "write"]
    
    return {
        "total_operations": readers_count + writers_count,
        "read_success": sum(1 for r in read_results if r["success"]),
        "write_success": sum(1 for r in write_results if r["success"]),
        "write_rejected": sum(1 for r in write_results if not r["success"]),
    }
