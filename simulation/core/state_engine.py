"""Traffic State Engine for Q-FLOW.
Extracts live TraCI telemetry from SUMO and compiles the official JSON data contract
consumed by Member 2 (Quantum Optimizer) and Member 4 (Dashboard).
"""

import time
from typing import Dict, Any, Set
import traci

from shared.config.simulation_config import (
    JUNCTION_IDS,
    JUNCTION_APPROACHES,
    NETWORK_EDGES,
    DEFAULT_EDGE_CAPACITY,
)
from shared.schemas.traffic_state import TrafficState, JunctionState, EdgeState, GlobalTrafficState
from simulation.core.metrics import SimulationMetricsTracker


class TrafficStateEngine:
    """Compiles normalized traffic state snapshots from active TraCI connection."""

    def __init__(self, metrics_tracker: SimulationMetricsTracker):
        self.metrics_tracker = metrics_tracker
        self.closed_edges: Set[str] = set()
        self.junction_throughput: Dict[str, int] = {j_id: 0 for j_id in JUNCTION_IDS}
        self.last_edge_vehicles: Dict[str, Set[str]] = {edge_id: set() for edge_id in NETWORK_EDGES}

    def set_edge_status(self, edge_id: str, is_closed: bool):
        """Update internal tracking of edge operational status."""
        if is_closed:
            self.closed_edges.add(edge_id)
        else:
            self.closed_edges.discard(edge_id)

    def extract_state(self) -> Dict[str, Any]:
        """Query TraCI and return the official TrafficState dictionary."""
        sim_time = traci.simulation.getTime()
        now_ts = time.time()

        # 1. Edge telemetry
        edges_data: Dict[str, Dict[str, Any]] = {}
        total_vehicles = 0
        total_halting = 0
        speed_sum = 0.0
        active_edge_count = 0
        step_fuel_ml = 0.0
        step_co2_g = 0.0

        for edge_id in NETWORK_EDGES:
            try:
                v_count = traci.edge.getLastStepVehicleNumber(edge_id)
                halt_count = traci.edge.getLastStepHaltingNumber(edge_id)
                mean_speed_mps = traci.edge.getLastStepMeanSpeed(edge_id)
                # m/s to km/h; if no vehicles, mean_speed is -1 or 0 in SUMO
                speed_kmh = max(0.0, mean_speed_mps * 3.6) if v_count > 0 else 50.0

                fuel_mg_s = traci.edge.getFuelConsumption(edge_id)
                co2_mg_s = traci.edge.getCO2Emission(edge_id)
                # Convert mg to ml (gasoline density ~ 0.74 g/ml -> 740 mg/ml) and mg to g
                step_fuel_ml += fuel_mg_s / 740.0
                step_co2_g += co2_mg_s / 1000.0

                current_vids = set(traci.edge.getLastStepVehicleIDs(edge_id))
                departed_from_edge = len(self.last_edge_vehicles[edge_id] - current_vids)
                self.last_edge_vehicles[edge_id] = current_vids

                capacity = DEFAULT_EDGE_CAPACITY
                density = min(1.0, round(v_count / capacity, 4))
                status = "CLOSED" if edge_id in self.closed_edges else "OPEN"

                edges_data[edge_id] = {
                    "vehicle_count": v_count,
                    "queue_length": halt_count,
                    "density": density,
                    "average_speed": round(speed_kmh, 2),
                    "capacity": capacity,
                    "status": status,
                }

                total_vehicles += v_count
                total_halting += halt_count
                if v_count > 0:
                    speed_sum += speed_kmh * v_count
                    active_edge_count += v_count

            except traci.TraCIException:
                edges_data[edge_id] = {
                    "vehicle_count": 0,
                    "queue_length": 0,
                    "density": 0.0,
                    "average_speed": 50.0,
                    "capacity": DEFAULT_EDGE_CAPACITY,
                    "status": "OPEN",
                }

        # 2. Junction telemetry
        junctions_data: Dict[str, Dict[str, Any]] = {}
        for j_id in JUNCTION_IDS:
            approaches = JUNCTION_APPROACHES.get(j_id, {"NS": [], "EW": []})

            queue_ns = sum(edges_data.get(e, {}).get("queue_length", 0) for e in approaches["NS"])
            queue_ew = sum(edges_data.get(e, {}).get("queue_length", 0) for e in approaches["EW"])

            ns_densities = [edges_data.get(e, {}).get("density", 0.0) for e in approaches["NS"]]
            ew_densities = [edges_data.get(e, {}).get("density", 0.0) for e in approaches["EW"]]
            all_densities = ns_densities + ew_densities
            avg_density = round(sum(all_densities) / len(all_densities), 4) if all_densities else 0.0

            ns_speeds = [edges_data.get(e, {}).get("average_speed", 0.0) for e in approaches["NS"]]
            ew_speeds = [edges_data.get(e, {}).get("average_speed", 0.0) for e in approaches["EW"]]
            all_speeds = ns_speeds + ew_speeds
            avg_speed = round(sum(all_speeds) / len(all_speeds), 2) if all_speeds else 0.0

            # Waiting time across incoming lanes
            total_waiting = 0.0
            vehicle_in_approach = 0
            for edge in approaches["NS"] + approaches["EW"]:
                try:
                    total_waiting += traci.edge.getWaitingTime(edge)
                    vehicle_in_approach += traci.edge.getLastStepVehicleNumber(edge)
                except traci.TraCIException:
                    pass
            mean_waiting = round(total_waiting / max(1, vehicle_in_approach), 2)

            # Signal state string
            signal_name = "NS_GREEN"
            try:
                phase_idx = traci.trafficlight.getPhase(j_id)
                # Standard mapping: 0,1 -> NS; 3,4 -> EW; 2,5 -> Yellow
                if phase_idx in (0, 1):
                    signal_name = "NS_GREEN"
                elif phase_idx in (3, 4):
                    signal_name = "EW_GREEN"
                elif phase_idx == 2:
                    signal_name = "NS_YELLOW"
                elif phase_idx == 5:
                    signal_name = "EW_YELLOW"
                else:
                    signal_name = f"PHASE_{phase_idx}"
            except traci.TraCIException:
                pass

            # Pedestrian waiting demand around junction
            ped_waiting = 0
            try:
                # Check persons on approach edges
                for edge in approaches["NS"] + approaches["EW"]:
                    persons = traci.edge.getLastStepPersonIDs(edge)
                    for pid in persons:
                        if traci.person.getWaitingTime(pid) > 0.5:
                            ped_waiting += 1
            except traci.TraCIException:
                pass

            # Update junction throughput
            # Approximate by vehicles departing incoming lanes
            junctions_data[j_id] = {
                "queue_ns": queue_ns,
                "queue_ew": queue_ew,
                "density": avg_density,
                "avg_speed": avg_speed,
                "waiting_time": mean_waiting,
                "throughput": self.junction_throughput[j_id],
                "signal": signal_name,
                "pedestrian_waiting": ped_waiting,
            }

        # 3. Global aggregates
        global_active = traci.vehicle.getIDCount()
        step_arrived = traci.simulation.getArrivedNumber()
        step_departed = traci.simulation.getDepartedNumber()

        global_avg_speed = round(speed_sum / max(1, active_edge_count), 2) if active_edge_count > 0 else 50.0

        # Global average waiting time
        all_vids = traci.vehicle.getIDList()
        total_veh_waiting = sum(traci.vehicle.getWaitingTime(vid) for vid in all_vids) if all_vids else 0.0
        global_avg_waiting = round(total_veh_waiting / max(1, len(all_vids)), 2)

        # Update cumulative metrics tracker
        self.metrics_tracker.update_step(
            active_vehicles=global_active,
            mean_speed=global_avg_speed / 3.6,
            total_queue=total_halting,
            mean_waiting_time=global_avg_waiting,
            step_arrived=step_arrived,
            step_departed=step_departed,
            step_fuel_ml=step_fuel_ml,
            step_co2_g=step_co2_g,
        )
        metrics_summary = self.metrics_tracker.get_summary()

        global_data = {
            "vehicle_count": global_active,
            "average_speed": global_avg_speed,
            "average_waiting_time": global_avg_waiting,
            "total_queue": total_halting,
            "throughput": metrics_summary["total_throughput"],
            "total_travel_time": metrics_summary["total_travel_time_s"],
            "fuel_consumption_ml": metrics_summary["total_fuel_consumption_ml"],
            "co2_emissions_g": metrics_summary["total_co2_emissions_g"],
        }

        # Structure payload
        raw_state = {
            "timestamp": now_ts,
            "simulation_time": sim_time,
            "junctions": junctions_data,
            "edges": edges_data,
            "global": global_data,
        }

        # Validate against Pydantic schema to guarantee 100% compliance with data contract
        validated = TrafficState.model_validate(raw_state)
        return validated.model_dump(by_alias=True)
