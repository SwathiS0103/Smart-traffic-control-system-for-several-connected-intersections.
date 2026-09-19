"""Traffic Simulation Controller for Q-FLOW.
Main entry point providing high-level TraCI control, state extraction,
signal plan updates, road closures, and emergency vehicle injection.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import traci

from shared.config.simulation_config import (
    JUNCTION_IDS,
    NETWORK_EDGES,
    DEFAULT_SPEED_LIMIT_MPS,
)
from shared.schemas.signal_plan import SignalPlan
from simulation.core.metrics import SimulationMetricsTracker
from simulation.core.state_engine import TrafficStateEngine
from simulation.core.mock_simulation import MockTrafficSimulation
from simulation.scenarios.scenario_manager import load_scenario


class TrafficSimulation:
    """Traffic Digital Twin simulation controller using SUMO TraCI."""

    def __init__(self, mock: bool = False, scenario: str = "normal"):
        self.mock_mode = mock
        self.scenario = scenario
        self.is_running = False
        self._mock_sim: Optional[MockTrafficSimulation] = None

        if self.mock_mode:
            self._mock_sim = MockTrafficSimulation(scenario=scenario)

        # Paths
        base_dir = Path(__file__).resolve().parent.parent
        self.net_file = base_dir / "network" / "network.net.xml"
        self.cfg_file = base_dir / "network" / "qflow.sumocfg"

        # Components
        self.metrics_tracker = SimulationMetricsTracker()
        self.state_engine = TrafficStateEngine(self.metrics_tracker)
        self.route_counter = 0

    def start(self, gui: bool = False, scenario: Optional[str] = None):
        """Start the SUMO simulation session and connect TraCI.

        Args:
            gui: If True, launch sumo-gui instead of headless sumo.
            scenario: Name of scenario ('normal', 'heavy_traffic', 'emergency', 'road_closure').
        """
        if scenario:
            self.scenario = scenario

        if self.mock_mode:
            self.is_running = True
            return self._mock_sim.start(gui=gui, scenario=self.scenario)

        if self.is_running:
            return True

        route_file = load_scenario(self.scenario)

        sumo_binary = "sumo-gui" if gui else "sumo"
        # Check if binary exists
        if shutil.which(sumo_binary) is None:
            sumo_binary = "sumo"

        sumo_cmd = [
            sumo_binary,
            "-n", str(self.net_file),
            "-r", str(route_file),
            "--step-length", "1.0",
            "--time-to-teleport", "-1",
            "--ignore-route-errors", "true",
            "--device.rerouting.adaptation-interval", "1",
            "--device.rerouting.probability", "1.0",
            "--no-step-log", "true",
            "--no-warnings", "true",
        ]

        if gui:
            sumo_cmd.extend(["--start", "true", "--quit-on-end", "true"])

        try:
            traci.start(sumo_cmd)
            self.is_running = True
            self.metrics_tracker.reset()
        except Exception as e:
            # Fallback to mock mode if SUMO binary / port fails
            print(f"[TrafficSimulation] Warning: TraCI launch failed ({e}). Falling back to Mock mode.")
            self.mock_mode = True
            self._mock_sim = MockTrafficSimulation(scenario=self.scenario)
            self._mock_sim.start(gui=gui, scenario=self.scenario)
            self.is_running = True

        return True

    def step(self, steps: int = 1):
        """Advance the simulation by given number of steps (seconds)."""
        if not self.is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")

        if self.mock_mode:
            return self._mock_sim.step(steps=steps)

        for _ in range(steps):
            traci.simulationStep()

    def stop(self):
        """Safely terminate the simulation and close the TraCI connection."""
        if not self.is_running:
            return

        if self.mock_mode:
            self._mock_sim.stop()
            self.is_running = False
            return

        try:
            traci.close()
        except Exception:
            pass
        finally:
            self.is_running = False

    def get_traffic_state(self) -> Dict[str, Any]:
        """Collect and return full TrafficState JSON data contract."""
        if not self.is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")

        if self.mock_mode:
            return self._mock_sim.get_traffic_state()

        return self.state_engine.extract_state()

    def get_junction_state(self, junction_id: str) -> Dict[str, Any]:
        """Get state for a specific junction."""
        state = self.get_traffic_state()
        if junction_id not in state["junctions"]:
            raise ValueError(f"Junction '{junction_id}' not found. Valid: {JUNCTION_IDS}")
        return state["junctions"][junction_id]

    def get_edge_state(self, edge_id: str) -> Dict[str, Any]:
        """Get state for a specific edge."""
        state = self.get_traffic_state()
        if edge_id not in state["edges"]:
            raise ValueError(f"Edge '{edge_id}' not found. Valid: {NETWORK_EDGES}")
        return state["edges"][edge_id]

    def apply_signal_plan(self, signal_plan: Union[Dict[str, Any], SignalPlan]):
        """Update traffic signal green times in SUMO using Member 2's signal plan.

        Expected signal_plan format:
        {
          "signal_plan": {
            "J1": { "NS_green": 40.0, "EW_green": 20.0 },
            "J2": { "NS_green": 25.0, "EW_green": 35.0 }
          }
        }
        """
        if not self.is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")

        if self.mock_mode:
            return self._mock_sim.apply_signal_plan(signal_plan)

        # Validate with SignalPlan schema if dict
        if isinstance(signal_plan, dict):
            validated = SignalPlan.model_validate(signal_plan)
            plan_dict = validated.signal_plan
        else:
            plan_dict = signal_plan.signal_plan

        for j_id, timing in plan_dict.items():
            if j_id not in JUNCTION_IDS:
                continue

            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    logics = traci.trafficlight.getCompleteRedYellowGreenDefinition(j_id)
                    if not logics:
                        continue

                    logic = logics[0]
                    # In standard network generated by netconvert:
                    # Phase 0: NS Green
                    # Phase 1: NS Green transition / clearing
                    # Phase 2: NS Yellow
                    # Phase 3: EW Green
                    # Phase 4: EW Green transition / clearing
                    # Phase 5: EW Yellow
                    if len(logic.phases) >= 4:
                        logic.phases[0].duration = float(timing.NS_green)
                        # If 6 phases (with transition phase 1 & 4), keep transitions fixed at 3-5s
                        ew_phase_idx = 3 if len(logic.phases) >= 6 else 2
                        logic.phases[ew_phase_idx].duration = float(timing.EW_green)

                        traci.trafficlight.setCompleteRedYellowGreenDefinition(j_id, logic)
            except traci.TraCIException as e:
                print(f"[TrafficSimulation] Warning: Failed to apply signal plan for {j_id}: {e}")

    def close_edge(self, edge_id: str):
        """Close an edge to traffic in SUMO and update state reporting to CLOSED."""
        if not self.is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")

        if edge_id not in NETWORK_EDGES:
            raise ValueError(f"Unknown edge '{edge_id}'. Valid: {NETWORK_EDGES}")

        if self.mock_mode:
            return self._mock_sim.close_edge(edge_id)

        try:
            # Inform routing engine that this edge has infinite travel time
            traci.edge.adaptTraveltime(edge_id, 1000000.0)

            # Lower max speed so vehicles do not enter
            lane_count = traci.edge.getLaneNumber(edge_id)
            for i in range(lane_count):
                lane_id = f"{edge_id}_{i}"
                traci.lane.setMaxSpeed(lane_id, 0.1)

            self.state_engine.set_edge_status(edge_id, is_closed=True)

            # Reroute active vehicles whose current route contains this edge
            active_vids = traci.vehicle.getIDList()
            for vid in active_vids:
                try:
                    veh_route = traci.vehicle.getRoute(vid)
                    if edge_id in veh_route:
                        traci.vehicle.rerouteTraveltime(vid)
                except traci.TraCIException:
                    pass
        except traci.TraCIException as e:
            print(f"[TrafficSimulation] Error closing edge {edge_id}: {e}")

    def open_edge(self, edge_id: str):
        """Reopen an edge in SUMO and restore its state to OPEN."""
        if not self.is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")

        if edge_id not in NETWORK_EDGES:
            raise ValueError(f"Unknown edge '{edge_id}'. Valid: {NETWORK_EDGES}")

        if self.mock_mode:
            return self._mock_sim.open_edge(edge_id)

        try:
            # Restore default travel time calculation
            traci.edge.adaptTraveltime(edge_id, -1.0)

            lane_count = traci.edge.getLaneNumber(edge_id)
            for i in range(lane_count):
                lane_id = f"{edge_id}_{i}"
                traci.lane.setMaxSpeed(lane_id, DEFAULT_SPEED_LIMIT_MPS)

            self.state_engine.set_edge_status(edge_id, is_closed=False)
        except traci.TraCIException as e:
            print(f"[TrafficSimulation] Error opening edge {edge_id}: {e}")

    def add_emergency_vehicle(
        self,
        route: Union[List[str], str],
        vehicle_id: Optional[str] = None
    ) -> str:
        """Inject an emergency vehicle into the network."""
        if not self.is_running:
            raise RuntimeError("Simulation is not running. Call start() first.")

        if self.mock_mode:
            return self._mock_sim.add_emergency_vehicle(route, vehicle_id)

        route_edges = route if isinstance(route, list) else route.strip().split()
        self.route_counter += 1
        route_id = f"dynamic_em_route_{self.route_counter}"
        v_id = vehicle_id or f"emergency_{self.route_counter}"

        try:
            traci.route.add(route_id, route_edges)
            traci.vehicle.add(
                v_id,
                route_id,
                typeID="emergency",
                depart="now",
                departLane="first",
                departPos="base"
            )
            # High-visibility emergency vehicle styling
            traci.vehicle.setColor(v_id, (255, 0, 0, 255))
            traci.vehicle.setSpeedMode(v_id, 31)  # Enable emergency vehicle speed privileges
            return v_id
        except traci.TraCIException as e:
            print(f"[TrafficSimulation] Error inserting emergency vehicle: {e}")
            return v_id

    def get_metrics(self) -> Dict[str, Any]:
        """Return cumulative metrics summary."""
        if self.mock_mode:
            return self._mock_sim.get_metrics()
        return self.metrics_tracker.get_summary()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
