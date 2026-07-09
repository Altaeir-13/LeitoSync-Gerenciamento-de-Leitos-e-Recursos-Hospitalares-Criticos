from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from sqlalchemy import select, func
from app.repositories.resource_repo import ResourceRepository
from app.models.resource import Resource
from app.models.hospital import Hospital
from app.models.resource_type import ResourceType
from app.models.audit_log import AuditLog
from app.schemas.base import ReservationCreate, ActionRequest, ResourceResponse, ResourceDetailResponse, HospitalResponse, ResourceTypeResponse, AuditLogResponse
from app.core.enums import ResourceStatus
from app.routes.ws import manager

async def sistema_health(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "ok"}

async def hospitais_listar(db: AsyncSession, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    res = await db.execute(select(Hospital))
    hospitals = res.scalars().all()
    return [HospitalResponse.model_validate(h).model_dump(mode="json") for h in hospitals]

async def tipos_recursos_listar(db: AsyncSession, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    res = await db.execute(select(ResourceType))
    types = res.scalars().all()
    return [ResourceTypeResponse.model_validate(t).model_dump(mode="json") for t in types]

async def recursos_listar(db: AsyncSession, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    resources = await ResourceRepository.get_all(db)
    return [ResourceResponse.model_validate(r).model_dump(mode="json") for r in resources]

async def recursos_obter(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    resource = await ResourceRepository.get_by_id(db, params["resource_id"])
    return ResourceDetailResponse.model_validate(resource).model_dump(mode="json")

async def recursos_disponibilidade(db: AsyncSession, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    resources = await ResourceRepository.get_all(db)
    available = [r for r in resources if r.status == ResourceStatus.AVAILABLE]
    return [ResourceResponse.model_validate(r).model_dump(mode="json") for r in available]

async def dashboard_resumo(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    total_hosp = await db.scalar(select(func.count(Hospital.id))) or 0
    resources = await ResourceRepository.get_all(db)
    total_res = len(resources)
    
    counts = {
        ResourceStatus.AVAILABLE: 0,
        ResourceStatus.RESERVED: 0,
        ResourceStatus.OCCUPIED: 0,
        ResourceStatus.BLOCKED: 0,
        ResourceStatus.MAINTENANCE: 0,
    }
    for r in resources:
        if r.status in counts:
            counts[r.status] += 1
            
    return {
        "total_hospitals": total_hosp,
        "total_resources": total_res,
        "available": counts[ResourceStatus.AVAILABLE],
        "reserved": counts[ResourceStatus.RESERVED],
        "occupied": counts[ResourceStatus.OCCUPIED],
        "blocked": counts[ResourceStatus.BLOCKED],
        "maintenance": counts[ResourceStatus.MAINTENANCE],
        "occupancy_rate": (counts[ResourceStatus.OCCUPIED] / total_res * 100) if total_res > 0 else 0
    }

async def auditoria_listar(db: AsyncSession, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    res = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100))
    logs = res.scalars().all()
    return [AuditLogResponse.model_validate(l).model_dump(mode="json") for l in logs]

async def recursos_reservar(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    req = ReservationCreate(**params)
    resource = await ResourceRepository.reserve(db, params["resource_id"], req)
    await db.commit()
    await db.refresh(resource)
    await manager.broadcast_resource_update(resource.id, resource.status.value)
    return {"success": True, "message": "Recurso reservado com sucesso.", "resource": ResourceResponse.model_validate(resource).model_dump(mode="json")}

async def _change_status(db: AsyncSession, resource_id: int, new_status: ResourceStatus, params: Dict[str, Any]) -> Dict[str, Any]:
    req = ActionRequest(**params)
    resource = await ResourceRepository.change_status(db, resource_id, new_status, req)
    await db.commit()
    await db.refresh(resource)
    await manager.broadcast_resource_update(resource.id, resource.status.value)
    return {"success": True, "message": f"Status alterado para {new_status.value}", "resource": ResourceResponse.model_validate(resource).model_dump(mode="json")}

async def recursos_liberar(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await _change_status(db, params["resource_id"], ResourceStatus.AVAILABLE, params)

async def recursos_ocupar(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await _change_status(db, params["resource_id"], ResourceStatus.OCCUPIED, params)

async def recursos_bloquear(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await _change_status(db, params["resource_id"], ResourceStatus.BLOCKED, params)

async def recursos_manutencao(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await _change_status(db, params["resource_id"], ResourceStatus.MAINTENANCE, params)

# Simulacoes
from app.routes.simulation import run_readers, run_writers, run_readers_writers

async def simulacao_leitores(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await run_readers(params["resource_id"], params.get("count", 10))

async def simulacao_escritores(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await run_writers(params["resource_id"], params.get("count", 5))

async def simulacao_leitores_escritores(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    return await run_readers_writers(params["resource_id"], params.get("readers_count", 10), params.get("writers_count", 5))
