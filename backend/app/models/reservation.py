from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.enums import ReservationPriority, ReservationStatus

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    requester_name = Column(String, nullable=False)
    patient_code = Column(String, nullable=True)
    priority = Column(Enum(ReservationPriority), default=ReservationPriority.MEDIUM)
    reason = Column(String, nullable=True)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    resource = relationship("Resource", back_populates="reservations")
