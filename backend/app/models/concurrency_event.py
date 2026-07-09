from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from app.database import Base

class ConcurrencyEvent(Base):
    __tablename__ = "concurrency_events"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    operation_type = Column(String, nullable=False)
    success = Column(Boolean, default=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
