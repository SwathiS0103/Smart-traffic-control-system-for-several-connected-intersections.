from typing import Dict, List, Optional
from .event_models import EmergencyVehicle, EmergencyVehicleStatus

class EmergencyManager:
    """Tracks and manages active emergency vehicles."""
    
    def __init__(self):
        self.active_emergencies: Dict[str, EmergencyVehicle] = {}

    def dispatch_vehicle(self, vehicle: EmergencyVehicle) -> None:
        """Register a new emergency vehicle."""
        self.active_emergencies[vehicle.vehicle_id] = vehicle

    def update_vehicle_status(self, vehicle_id: str, status: EmergencyVehicleStatus) -> None:
        """Update vehicle status (e.g., passing, completed)."""
        if vehicle_id in self.active_emergencies:
            self.active_emergencies[vehicle_id].status = status

    def update_location(self, vehicle_id: str, location: str, eta: float) -> None:
        """Update vehicle current location and ETA to destination."""
        if vehicle_id in self.active_emergencies:
            veh = self.active_emergencies[vehicle_id]
            veh.current_location = location
            veh.eta_to_destination = eta

    def get_vehicle(self, vehicle_id: str) -> Optional[EmergencyVehicle]:
        return self.active_emergencies.get(vehicle_id)

    def get_active_vehicles(self) -> List[EmergencyVehicle]:
        """Return all vehicles currently in transit."""
        return [
            v for v in self.active_emergencies.values() 
            if v.status not in (EmergencyVehicleStatus.COMPLETED, EmergencyVehicleStatus.REROUTED)
        ]

    def remove_vehicle(self, vehicle_id: str) -> None:
        if vehicle_id in self.active_emergencies:
            del self.active_emergencies[vehicle_id]
