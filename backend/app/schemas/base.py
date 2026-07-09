from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.core.enums import ResourceStatus, ReservationPriority, ReservationStatus

class HospitalResponse(BaseModel):
    id: int
    name: str
    city: str
    state: str
    active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResourceTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ResourceResponse(BaseModel):
    id: int
    hospital_id: int
    resource_type_id: int
    code: str
    status: ResourceStatus
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResourceDetailResponse(ResourceResponse):
    hospital: Optional[HospitalResponse] = None
    resource_type: Optional[ResourceTypeResponse] = None
    model_config = ConfigDict(from_attributes=True)

class ReservationCreate(BaseModel):
    requester_name: str
    patient_code: Optional[str] = None
    priority: ReservationPriority = ReservationPriority.MEDIUM
    reason: Optional[str] = None

class ActionRequest(BaseModel):
    actor_name: str
    reason: Optional[str] = None

class DashboardSummaryResponse(BaseModel):
    total_hospitals: int
    total_resources: int
    available: int
    reserved: int
    occupied: int
    blocked: int
    maintenance: int
    occupancy_rate: float

class AuditLogResponse(BaseModel):
    id: int
    resource_id: int
    action: str
    old_status: Optional[str]
    new_status: str
    actor_name: str
    details: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConcurrencyEventResponse(BaseModel):
    id: int
    resource_id: int
    operation_type: str
    success: bool
    message: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
