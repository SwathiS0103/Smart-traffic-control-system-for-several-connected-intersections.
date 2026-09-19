from typing import Dict, Any
from .event_models import EventSeverity

class AccidentManager:
    """Manages accidents and their impact on road capacity."""
    
    def __init__(self):
        # Maps edge_id -> reduced_capacity_factor
        self.active_accidents: Dict[str, float] = {}
        
        self.severity_impact = {
            EventSeverity.LOW: 0.8,       # 20% capacity reduction
            EventSeverity.MEDIUM: 0.5,    # 50% capacity reduction
            EventSeverity.HIGH: 0.35,     # 65% capacity reduction
            EventSeverity.CRITICAL: 0.1   # 90% capacity reduction
        }

    def create_accident(self, edge_id: str, severity: EventSeverity) -> None:
        """Register an accident and its capacity factor."""
        factor = self.severity_impact.get(severity, 0.5)
        self.active_accidents[edge_id] = factor

    def update_accident(self, edge_id: str, severity: EventSeverity) -> None:
        """Update an existing accident severity."""
        if edge_id in self.active_accidents:
            self.create_accident(edge_id, severity)

    def estimate_capacity_reduction(self, edge_id: str, normal_capacity: float) -> float:
        """Return the new reduced capacity if an accident is active."""
        if edge_id in self.active_accidents:
            return normal_capacity * self.active_accidents[edge_id]
        return normal_capacity

    def resolve_accident(self, edge_id: str) -> None:
        """Remove accident constraint."""
        if edge_id in self.active_accidents:
            del self.active_accidents[edge_id]
