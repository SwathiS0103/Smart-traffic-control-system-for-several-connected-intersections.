"""Integration tests for SUMO TraCI TrafficSimulation in Q-FLOW.
Runs headless SUMO to verify 4-junction network loading, TraCI communication,
state engine extraction, signal plan modification, and road closures.
"""

import pytest
import shutil
from pathlib import Path

from shared.config.simulation_config import JUNCTION_IDS, NETWORK_EDGES
from shared.schemas.traffic_state import TrafficState
from simulation.core.traffic_simulation import TrafficSimulation

# Check if SUMO is available on the machine
SUMO_AVAILABLE = shutil.which("sumo") is not None


@pytest.mark.skipif(not SUMO_AVAILABLE, reason="SUMO binary not found in PATH")
def test_sumo_network_and_traci_lifecycle():
    sim = TrafficSimulation(mock=False, scenario="normal")
    assert not sim.is_running
    sim.start(gui=False)
    assert sim.is_running

    # Run 5 steps
    sim.step(5)

    state = sim.get_traffic_state()
    # Validate against Pydantic schema
    validated = TrafficState.model_validate(state)
    assert validated.simulation_time >= 5.0

    # Verify 4 junctions present
    assert set(state["junctions"].keys()) == set(JUNCTION_IDS)
    for j_id in JUNCTION_IDS:
        j_state = sim.get_junction_state(j_id)
        assert "queue_ns" in j_state
        assert "queue_ew" in j_state
        assert "signal" in j_state
        assert "density" in j_state
        assert 0.0 <= j_state["density"] <= 1.0

    # Verify all edges present
    for edge_id in NETWORK_EDGES:
        e_state = sim.get_edge_state(edge_id)
        assert "vehicle_count" in e_state
        assert "capacity" in e_state
        assert e_state["status"] == "OPEN"

    sim.stop()
    assert not sim.is_running


@pytest.mark.skipif(not SUMO_AVAILABLE, reason="SUMO binary not found in PATH")
def test_sumo_signal_plan_application():
    sim = TrafficSimulation(mock=False, scenario="normal")
    sim.start(gui=False)
    sim.step(3)

    plan = {
        "signal_plan": {
            "J1": {"NS_green": 42.0, "EW_green": 18.0},
            "J2": {"NS_green": 22.0, "EW_green": 38.0},
        }
    }
    sim.apply_signal_plan(plan)
    sim.step(3)
    sim.stop()


@pytest.mark.skipif(not SUMO_AVAILABLE, reason="SUMO binary not found in PATH")
def test_sumo_edge_closure_and_reopen():
    sim = TrafficSimulation(mock=False, scenario="normal")
    sim.start(gui=False)
    sim.step(5)

    sim.close_edge("J1_J2")
    state_closed = sim.get_edge_state("J1_J2")
    assert state_closed["status"] == "CLOSED"

    sim.step(5)

    sim.open_edge("J1_J2")
    state_open = sim.get_edge_state("J1_J2")
    assert state_open["status"] == "OPEN"

    sim.stop()


@pytest.mark.skipif(not SUMO_AVAILABLE, reason="SUMO binary not found in PATH")
def test_sumo_emergency_vehicle():
    sim = TrafficSimulation(mock=False, scenario="normal")
    sim.start(gui=False)
    sim.step(5)

    em_route = ["W1_J1", "J1_J2", "J2_E1"]
    v_id = sim.add_emergency_vehicle(em_route, vehicle_id="test_ambulance_01")
    assert v_id == "test_ambulance_01"

    sim.step(5)
    metrics = sim.get_metrics()
    assert "average_speed_kmh" in metrics
    assert "total_throughput" in metrics

    sim.stop()
