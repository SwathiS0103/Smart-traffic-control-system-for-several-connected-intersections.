"""Metrics computation and performance evaluation engine for Q-FLOW.
Tracks waiting time, queue lengths, average speed, throughput, emissions, and travel times.
"""

from typing import Dict, Any, List


class SimulationMetricsTracker:
    """Accumulates step-level and cumulative traffic performance metrics."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all tracked metrics to zero."""
        self.step_count: int = 0
        self.total_arrived_vehicles: int = 0
        self.total_departed_vehicles: int = 0
        self.cumulative_travel_time: float = 0.0
        self.cumulative_waiting_time: float = 0.0
        self.cumulative_fuel_ml: float = 0.0
        self.cumulative_co2_g: float = 0.0

        # Time-series history for computing accurate rolling averages
        self.speed_history: List[float] = []
        self.queue_history: List[int] = []
        self.active_vehicle_history: List[int] = []
        self.waiting_time_history: List[float] = []

    def update_step(
        self,
        active_vehicles: int,
        mean_speed: float,
        total_queue: int,
        mean_waiting_time: float,
        step_arrived: int,
        step_departed: int,
        step_fuel_ml: float = 0.0,
        step_co2_g: float = 0.0,
    ):
        """Record telemetry from an individual simulation time step."""
        self.step_count += 1
        self.total_arrived_vehicles += step_arrived
        self.total_departed_vehicles += step_departed

        self.cumulative_fuel_ml += step_fuel_ml
        self.cumulative_co2_g += step_co2_g

        self.speed_history.append(mean_speed)
        self.queue_history.append(total_queue)
        self.active_vehicle_history.append(active_vehicles)
        self.waiting_time_history.append(mean_waiting_time)

        # Approximate travel time accumulation for active + arrived vehicles
        self.cumulative_travel_time += active_vehicles * 1.0

    def get_summary(self) -> Dict[str, Any]:
        """Compute aggregate performance indicators across the entire simulation run."""
        avg_speed = (
            sum(self.speed_history) / len(self.speed_history)
            if self.speed_history
            else 0.0
        )
        avg_queue = (
            sum(self.queue_history) / len(self.queue_history)
            if self.queue_history
            else 0.0
        )
        avg_waiting = (
            sum(self.waiting_time_history) / len(self.waiting_time_history)
            if self.waiting_time_history
            else 0.0
        )
        avg_active = (
            sum(self.active_vehicle_history) / len(self.active_vehicle_history)
            if self.active_vehicle_history
            else 0.0
        )

        return {
            "total_steps": self.step_count,
            "total_throughput": self.total_arrived_vehicles,
            "total_departed": self.total_departed_vehicles,
            "average_speed_kmh": round(avg_speed * 3.6, 2),  # m/s to km/h
            "average_queue_length": round(avg_queue, 2),
            "average_waiting_time_s": round(avg_waiting, 2),
            "average_active_vehicles": round(avg_active, 2),
            "total_travel_time_s": round(self.cumulative_travel_time, 2),
            "total_fuel_consumption_ml": round(self.cumulative_fuel_ml, 2),
            "total_co2_emissions_g": round(self.cumulative_co2_g, 2),
        }
