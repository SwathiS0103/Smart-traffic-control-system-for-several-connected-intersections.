from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EventType(str, Enum):
    CONGESTION = "CONGESTION"
    ACCIDENT = "ACCIDENT"
    ROAD_CLOSURE = "ROAD_CLOSURE"
    EMERGENCY = "EMERGENCY"
    PEDESTRIAN_SURGE = "PEDESTRIAN_SURGE"

class EventSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EventStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"

class Event(BaseModel):
    event_id: str
    type: EventType
    location: str  # junction id or edge id (e.g. "J2", "J2_J3")
    severity: EventSeverity
    start_time: float
    duration: Optional[float] = None
    status: EventStatus = EventStatus.PENDING
    details: Dict[str, Any] = Field(default_factory=dict)
    
class EmergencyVehicleStatus(str, Enum):
    APPROACHING = "APPROACHING"
    AT_JUNCTION = "AT_JUNCTION"
    PASSING = "PASSING"
    COMPLETED = "COMPLETED"
    REROUTED = "REROUTED"

class EmergencyVehicle(BaseModel):
    vehicle_id: str
    type: str  # e.g., "AMBULANCE", "FIRE_TRUCK"
    origin: str
    destination: str
    route: List[str]
    priority: EventSeverity = EventSeverity.CRITICAL
    status: EmergencyVehicleStatus = EmergencyVehicleStatus.APPROACHING
    current_location: Optional[str] = None
    eta_to_destination: Optional[float] = None
