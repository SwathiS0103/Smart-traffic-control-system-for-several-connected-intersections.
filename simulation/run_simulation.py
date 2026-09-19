"""Demonstration runner for Q-FLOW Traffic Digital Twin simulation.
Executes an end-to-end run showcasing:
1. 4-intersection SUMO simulation with vehicles moving.
2. TraCI traffic-state JSON telemetry generation.
3. Dynamic application of Member 2's quantum signal plan.
4. Road closure (J1_J2) and state change verification.
5. Emergency vehicle injection (Ambulance).
6. Edge reopening and metrics report.
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from simulation.core.traffic_simulation import TrafficSimulation


def run_demo(steps: int = 40, scenario: str = "normal", gui: bool = False, mock: bool = False):
    print("=" * 70)
    print(f"  Q-FLOW Traffic Digital Twin Demonstration")
    print(f"  Mode: {'MOCK' if mock else 'SUMO TraCI'}")
    print(f"  Scenario: {scenario} | Steps: {steps} | GUI: {gui}")
    print("=" * 70)

    sim = TrafficSimulation(mock=mock, scenario=scenario)

    try:
        print("\n[1/6] Starting simulation...")
        sim.start(gui=gui, scenario=scenario)
        print("[OK] Simulation started and TraCI connected successfully.")

        # Step initial warmup
        print("\n[2/6] Running initial 10 simulation steps...")
        sim.step(10)
        state_step10 = sim.get_traffic_state()
        print(f"[OK] Elapsed Sim Time: {state_step10['simulation_time']}s")
        print(f"[OK] Active Vehicles: {state_step10['global']['vehicle_count']}")
        print(f"[OK] Network Mean Speed: {state_step10['global']['average_speed']} km/h")
        print("\n--- Sample Junction State (J1) ---")
        print(json.dumps(state_step10["junctions"]["J1"], indent=2))
        print("\n--- Sample Edge State (J1_J2) ---")
        print(json.dumps(state_step10["edges"]["J1_J2"], indent=2))

        # Member 2: Apply quantum signal plan
        print("\n[3/6] Applying Member 2 Quantum Signal Plan...")
        quantum_signal_plan = {
            "signal_plan": {
                "J1": {"NS_green": 45.0, "EW_green": 15.0},
                "J2": {"NS_green": 20.0, "EW_green": 40.0},
                "J3": {"NS_green": 35.0, "EW_green": 25.0},
                "J4": {"NS_green": 30.0, "EW_green": 30.0},
            }
        }
        sim.apply_signal_plan(quantum_signal_plan)
        print("[OK] Applied signal plan via TraCI:")
        print(json.dumps(quantum_signal_plan, indent=2))

        # Advance another 10 steps
        sim.step(10)

        # Member 3: Road closure on J1_J2
        print("\n[4/6] Simulating Road Incident: Closing edge 'J1_J2'...")
        sim.close_edge("J1_J2")
        state_closed = sim.get_edge_state("J1_J2")
        print(f"[OK] Edge J1_J2 Status after closure: {state_closed['status']}")
        assert state_closed["status"] == "CLOSED", "Edge status should be CLOSED!"

        # Advance 5 steps with closed road
        sim.step(5)

        # Member 3: Emergency Vehicle Dispatch
        print("\n[5/6] Dispatching Priority Emergency Vehicle (Ambulance)...")
        em_route = ["W1_J1", "J1_J3", "J3_J4", "J4_E2"]
        veh_id = sim.add_emergency_vehicle(route=em_route, vehicle_id="qflow_ambulance_01")
        print(f"[OK] Emergency vehicle '{veh_id}' injected along route: {' -> '.join(em_route)}")

        # Step 5 more steps
        sim.step(5)

        # Reopen edge
        print("\n[6/6] Incident cleared: Reopening edge 'J1_J2'...")
        sim.open_edge("J1_J2")
        state_reopened = sim.get_edge_state("J1_J2")
        print(f"[OK] Edge J1_J2 Status after reopening: {state_reopened['status']}")
        assert state_reopened["status"] == "OPEN", "Edge status should be OPEN!"

        # Final steps
        sim.step(max(1, steps - 30))

        final_state = sim.get_traffic_state()
        metrics = sim.get_metrics()

        print("\n" + "=" * 70)
        print("  Simulation Performance Summary Metrics")
        print("=" * 70)
        print(json.dumps(metrics, indent=2))

        print("\n" + "=" * 70)
        print("  Final Global Traffic State JSON")
        print("=" * 70)
        print(json.dumps(final_state["global"], indent=2))

        print("\n[OK] ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")

    finally:
        sim.stop()
        print("[OK] TraCI simulation session closed cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Q-FLOW Traffic Digital Twin simulation")
    parser.add_argument("--steps", type=int, default=35, help="Number of simulation steps")
    parser.add_argument("--scenario", type=str, default="normal", help="Scenario (normal, heavy_traffic, emergency, road_closure)")
    parser.add_argument("--gui", action="store_true", help="Launch SUMO GUI")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without SUMO")
    args = parser.parse_args()

    run_demo(steps=args.steps, scenario=args.scenario, gui=args.gui, mock=args.mock)
