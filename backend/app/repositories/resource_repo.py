from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import selectinload
from app.models.resource import Resource
from app.models.reservation import Reservation
from app.models.audit_log import AuditLog
from app.core.enums import ResourceStatus, ReservationStatus
from app.schemas.base import ReservationCreate, ActionRequest
from app.core.exceptions import ConcurrencyConflictException, ResourceNotFoundException, InvalidStateTransitionException

class ResourceRepository:
    
    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Resource).options(selectinload(Resource.hospital), selectinload(Resource.resource_type)))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, resource_id: int):
        result = await db.execute(
            select(Resource)
            .options(selectinload(Resource.hospital), selectinload(Resource.resource_type))
            .filter(Resource.id == resource_id)
        )
        resource = result.scalars().first()
        if not resource:
            raise ResourceNotFoundException()
        return resource

    @staticmethod
    async def reserve(db: AsyncSession, resource_id: int, req: ReservationCreate) -> Resource:
        try:
            # 1. & 2. Fetch with row-level lock (SELECT FOR UPDATE)
            # The transaction is already started by SQLAlchemy when db.execute is called within an async session.
            result = await db.execute(
                select(Resource).filter(Resource.id == resource_id).with_for_update()
            )
            resource = result.scalars().first()

            if not resource:
                raise ResourceNotFoundException()

            # 3. Check if status is available
            if getattr(resource.status, 'value', resource.status) != ResourceStatus.AVAILABLE.value:
                raise ConcurrencyConflictException()

            old_status = getattr(resource.status, 'value', resource.status)

            # 4. Alter status
            resource.status = ResourceStatus.RESERVED
            
            # 5. Increment version
            resource.version += 1

            # 6. Create Reservation
            reservation = Reservation(
                resource_id=resource.id,
                requester_name=req.requester_name,
                patient_code=req.patient_code,
                priority=req.priority,
                reason=req.reason,
                status=ReservationStatus.ACTIVE
            )
            db.add(reservation)

            # 7. Create AuditLog
            audit_log = AuditLog(
                resource_id=resource.id,
                action="RESERVE",
                old_status=old_status,
                new_status=ResourceStatus.RESERVED.value,
                actor_name=req.requester_name,
                details=req.reason
            )
            db.add(audit_log)

            # 8. Commit will be done in the service/route or by the caller
            return resource
        except DBAPIError as e:
            # Handle DB level concurrency errors if any
            raise ConcurrencyConflictException()

    @staticmethod
    async def change_status(db: AsyncSession, resource_id: int, new_status: ResourceStatus, req: ActionRequest) -> Resource:
        result = await db.execute(
            select(Resource).filter(Resource.id == resource_id).with_for_update()
        )
        resource = result.scalars().first()
        
        if not resource:
            raise ResourceNotFoundException()
            
        old_status = getattr(resource.status, 'value', resource.status)
        new_status_val = new_status.value
        
        if old_status == new_status_val:
            raise InvalidStateTransitionException(f"Resource is already {new_status_val}")

        resource.status = new_status
        resource.version += 1
        
        audit_log = AuditLog(
            resource_id=resource.id,
            action=new_status.name,
            old_status=old_status,
            new_status=new_status.value,
            actor_name=req.actor_name,
            details=req.reason
        )
        db.add(audit_log)
        
        return resource
