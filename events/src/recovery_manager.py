from typing import Dict, Any

class RecoveryManager:
    """Manages the transition period after an event ends to rebalance queues."""
    
    def __init__(self):
        self.active_recoveries: Dict[str, Dict[str, Any]] = {}

    def initiate_recovery(self, event_id: str, current_time: float, residual_queue: int) -> Dict[str, Any]:
        """Start a recovery period based on the remaining queue."""
        
        # Simple heuristic: 2 seconds of recovery time per vehicle in the residual queue
        # Base recovery time of 30 seconds
        recovery_duration = 30 + (residual_queue * 2)
        
        recovery_data = {
            "event_id": event_id,
            "start": current_time,
            "end": current_time + recovery_duration,
            "duration": recovery_duration,
            "residual_queue": residual_queue
        }
        
        self.active_recoveries[event_id] = recovery_data
        return {"recovery": recovery_data}

    def check_recoveries(self, current_time: float) -> list:
        """Check if any recoveries have completed."""
        completed = []
        for e_id, data in list(self.active_recoveries.items()):
            if current_time >= data["end"]:
                completed.append(e_id)
                del self.active_recoveries[e_id]
        return completed
