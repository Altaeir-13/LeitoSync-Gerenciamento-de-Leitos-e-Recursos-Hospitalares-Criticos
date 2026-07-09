from enum import Enum

class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    BLOCKED = "blocked"
    MAINTENANCE = "maintenance"

class ReservationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class ReservationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    ADMIN = "admin"
    REGULATOR = "regulator"
    HOSPITAL_OPERATOR = "hospital_operator"
    VIEWER = "viewer"
