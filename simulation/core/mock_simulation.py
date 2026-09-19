"""Mock Traffic Simulation Engine for Q-FLOW.
Provides realistic synthetic traffic telemetry adhering 100% to the official JSON schema.
Allows Member 2 (Quantum Optimizer) and Member 4 (Dashboard) to develop and test offline
without requiring SUMO installed.
"""

import time
import math
import random
from typing import Dict, Any, List, Optional, Set

from shared.config.simulation_config import (
    JUNCTION_IDS,
    JUNCTION_APPROACHES,
    NETWORK_EDGES,
    DEFAULT_EDGE_CAPACITY,
)
from shared.schemas.traffic_state import TrafficState
from simulation.core.metrics import SimulationMetricsTracker


class MockTrafficSimulation:
    """Simulates a 4-intersection traffic digital twin without requiring SUMO/TraCI."""

    def __init__(self, scenario: str = "normal"):
        self.scenario = scenario
        self.is_running = False
        self.sim_time = 0.0
        self.closed_edges: Set[str] = set()
        self.emergency_vehicles: List[Dict[str, Any]] = []
        self.metrics_tracker = SimulationMetricsTracker()

        # Signal phase allocations per junction (default: 30s NS, 30s EW)
        self.signal_timings: Dict[str, Dict[str, float]] = {
            j_id: {"NS_green": 30.0, "EW_green": 30.0} for j_id in JUNCTION_IDS
        }

        # Dynamic state generators
        self._init_state()

    def _init_state(self):
        """Initialize mock queues and vehicle distributions."""
        self.sim_time = 0.0
        self.closed_edges.clear()
        self.emergency_vehicles.clear()
        self.metrics_tracker.reset()

    def start(self, gui: bool = False, scenario: Optional[str] = None):
        """Start mock simulation session."""
        if scenario:
            self.scenario = scenario
        self.is_running = True
        self._init_state()
        return True

    def step(self, steps: int = 1):
        """Advance mock simulation by specified step count."""
        if not self.is_running:
            raise RuntimeError("Simulation has not been started. Call start() first.")

        for _ in range(steps):
            self.sim_time += 1.0

            # Mock arrivals and departures
            step_arrived = random.randint(0, 2)
            step_departed = random.randint(0, 2)
            active_count = 30 + int(10 * math.sin(self.sim_time / 20.0))

            self.metrics_tracker.update_step(
                active_vehicles=active_count,
                mean_speed=7.5,
                total_queue=random.randint(5, 20),
                mean_waiting_time=15.0,
                step_arrived=step_arrived,
                step_departed=step_departed,
                step_fuel_ml=12.5,
                step_co2_g=28.4,
            )

    def stop(self):
        """Stop mock simulation session."""
        self.is_running = False

    def get_traffic_state(self) -> Dict[str, Any]:
        """Compile and return current traffic state adhering 100% to JSON contract."""
        now_ts = time.time()
        edges_data: Dict[str, Dict[str, Any]] = {}
        total_vehicles = 0
        total_queue = 0
        speed_sum = 0.0

        for edge_id in NETWORK_EDGES:
            is_closed = edge_id in self.closed_edges

            if is_closed:
                v_count = 0
                q_len = 0
                density = 0.0
                speed = 0.0
                status = "CLOSED"
            else:
                # Oscillating realistic synthetic traffic based on scenario
                base_mult = 1.8 if self.scenario == "heavy_traffic" else 1.0
                wave = (math.sin(self.sim_time / 15.0 + hash(edge_id) % 10) + 1.0) / 2.0
                v_count = int(base_mult * (5 + wave * 18))
                q_len = int(v_count * (0.3 + 0.2 * wave))
                density = min(1.0, round(v_count / DEFAULT_EDGE_CAPACITY, 4))
                speed = round(max(5.0, 48.0 - (density * 35.0)), 2)
                status = "OPEN"

            edges_data[edge_id] = {
                "vehicle_count": v_count,
                "queue_length": q_len,
                "density": density,
                "average_speed": speed,
                "capacity": DEFAULT_EDGE_CAPACITY,
                "status": status,
            }

            total_vehicles += v_count
            total_queue += q_len
            speed_sum += speed

        avg_speed = round(speed_sum / len(NETWORK_EDGES), 2)

        # Junctions telemetry
        junctions_data: Dict[str, Dict[str, Any]] = {}
        for j_id in JUNCTION_IDS:
            approaches = JUNCTION_APPROACHES.get(j_id, {"NS": [], "EW": []})

            q_ns = sum(edges_data[e]["queue_length"] for e in approaches["NS"] if e in edges_data)
            q_ew = sum(edges_data[e]["queue_length"] for e in approaches["EW"] if e in edges_data)

            densities = [edges_data[e]["density"] for e in approaches["NS"] + approaches["EW"] if e in edges_data]
            avg_density = round(sum(densities) / len(densities), 4) if densities else 0.0

            speeds = [edges_data[e]["average_speed"] for e in approaches["NS"] + approaches["EW"] if e in edges_data]
            avg_j_speed = round(sum(speeds) / len(speeds), 2) if speeds else 0.0

            # Signal state based on current cycle
            timings = self.signal_timings[j_id]
            cycle_length = timings["NS_green"] + 3.0 + timings["EW_green"] + 3.0
            cycle_pos = self.sim_time % cycle_length

            if cycle_pos < timings["NS_green"]:
                sig = "NS_GREEN"
            elif cycle_pos < timings["NS_green"] + 3.0:
                sig = "NS_YELLOW"
            elif cycle_pos < timings["NS_green"] + 3.0 + timings["EW_green"]:
                sig = "EW_GREEN"
            else:
                sig = "EW_YELLOW"

            ped_wait = random.randint(0, 4) if self.sim_time > 10 else 0

            junctions_data[j_id] = {
                "queue_ns": q_ns,
                "queue_ew": q_ew,
                "density": avg_density,
                "avg_speed": avg_j_speed,
                "waiting_time": round(float(q_ns + q_ew) * 1.8, 2),
                "throughput": int(self.sim_time * 0.4),
                "signal": sig,
                "pedestrian_waiting": ped_wait,
            }

        metrics_sum = self.metrics_tracker.get_summary()

        raw_state = {
            "timestamp": time.time(),
            "simulation_time": self.sim_time,
            "junctions": junctions_data,
            "edges": edges_data,
            "global": {
                "vehicle_count": total_vehicles,
                "average_speed": avg_speed,
                "average_waiting_time": round(float(total_queue) * 1.5, 2),
                "total_queue": total_queue,
                "throughput": metrics_sum["total_throughput"],
                "total_travel_time": metrics_sum["total_travel_time_s"],
                "fuel_consumption_ml": metrics_sum["total_fuel_consumption_ml"],
                "co2_emissions_g": metrics_sum["total_co2_emissions_g"],
            },
        }

        # Validate with Pydantic model
        validated = TrafficState.model_validate(raw_state)
        return validated.model_dump(by_alias=True)

    def get_junction_state(self, junction_id: str) -> Dict[str, Any]:
        """Return state of a single junction."""
        state = self.get_traffic_state()
        if junction_id not in state["junctions"]:
            raise ValueError(f"Junction '{junction_id}' not found. Valid junctions: {JUNCTION_IDS}")
        return state["junctions"][junction_id]

    def get_edge_state(self, edge_id: str) -> Dict[str, Any]:
        """Return state of a single edge."""
        state = self.get_traffic_state()
        if edge_id not in state["edges"]:
            raise ValueError(f"Edge '{edge_id}' not found. Valid edges: {NETWORK_EDGES}")
        return state["edges"][edge_id]

    def apply_signal_plan(self, signal_plan: Dict[str, Any]):
        """Apply quantum/adaptive signal plan to junctions."""
        plan_dict = signal_plan.get("signal_plan", signal_plan)
        for j_id, timing in plan_dict.items():
            if j_id in self.signal_timings:
                self.signal_timings[j_id]["NS_green"] = float(timing.get("NS_green", 30.0))
                self.signal_timings[j_id]["EW_green"] = float(timing.get("EW_green", 30.0))

    def close_edge(self, edge_id: str):
        """Close an edge to traffic."""
        if edge_id not in NETWORK_EDGES:
            raise ValueError(f"Unknown edge '{edge_id}'. Valid edges: {NETWORK_EDGES}")
        self.closed_edges.add(edge_id)

    def open_edge(self, edge_id: str):
        """Reopen a previously closed edge."""
        self.closed_edges.discard(edge_id)

    def add_emergency_vehicle(self, route: Any, vehicle_id: Optional[str] = None) -> str:
        """Inject priority emergency vehicle."""
        v_id = vehicle_id or f"mock_ambulance_{len(self.emergency_vehicles) + 1}"
        route_list = route if isinstance(route, list) else route.split()
        self.emergency_vehicles.append({
            "id": v_id,
            "route": route_list,
            "inserted_at": self.sim_time,
        })
        return v_id

    def get_metrics(self) -> Dict[str, Any]:
        """Return overall metrics summary."""
        return self.metrics_tracker.get_summary()
