from typing import Dict, Any

class CongestionPredictor:
    """Predicts queue growth over time based on arrival/departure rates."""

    def predict_queue(self, junction_id: str, state: Dict[str, Any], event_severity: str = "LOW") -> Dict[str, Any]:
        """
        Estimate queue after 30s, 60s, 120s.
        Uses a basic deterministic queuing model: Q(t) = Q(0) + (ArrivalRate - DepartureRate) * t
        """
        # Parse current state
        q_ns = state.get("queue_ns", 0)
        q_ew = state.get("queue_ew", 0)
        current_queue = q_ns + q_ew
        
        # Estimate rates. If not provided, we infer from density and speed.
        # This is a naive model for the hackathon prototype.
        density = state.get("density", 0.5)
        
        # Arrival rate (vehicles/sec)
        # Higher density implies higher arrival rate
        arrival_rate = density * 1.5 
        
        # Departure rate (vehicles/sec)
        # Assuming nominal departure rate is 1 vehicle per 2 seconds of green time
        # We'll just use a base rate of 0.5 veh/sec, modified by severity
        base_departure = 0.5
        
        severity_impact = {
            "LOW": 1.0,
            "MEDIUM": 0.8,
            "HIGH": 0.5,
            "CRITICAL": 0.2
        }
        
        departure_rate = base_departure * severity_impact.get(event_severity, 1.0)
        
        net_rate = arrival_rate - departure_rate
        
        # Calculate future queues
        def calc_q(t: int) -> int:
            q = current_queue + (net_rate * t)
            return max(0, int(q))
            
        return {
            "junction": junction_id,
            "prediction": {
                "30s": calc_q(30),
                "60s": calc_q(60),
                "120s": calc_q(120)
            }
        }
