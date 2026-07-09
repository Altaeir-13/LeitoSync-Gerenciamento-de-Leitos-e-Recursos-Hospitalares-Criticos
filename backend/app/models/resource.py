from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.enums import ResourceStatus

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    resource_type_id = Column(Integer, ForeignKey("resource_types.id"), nullable=False)
    code = Column(String, nullable=False, index=True)
    status = Column(Enum(ResourceStatus), default=ResourceStatus.AVAILABLE, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hospital = relationship("Hospital", back_populates="resources")
    resource_type = relationship("ResourceType", back_populates="resources")
    reservations = relationship("Reservation", back_populates="resource")
    audit_logs = relationship("AuditLog", back_populates="resource")
