from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class ResourceType(Base):
    __tablename__ = "resource_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    resources = relationship("Resource", back_populates="resource_type")
