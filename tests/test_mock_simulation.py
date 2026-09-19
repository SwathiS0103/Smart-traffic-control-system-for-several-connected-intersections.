"""Unit tests for MockTrafficSimulation and Schema Validation in Q-FLOW.
Tests mock mode, JSON contract integrity, edge closures, emergency vehicles, and signal plans.
"""

import pytest
from shared.config.simulation_config import JUNCTION_IDS, NETWORK_EDGES
from shared.schemas.traffic_state import TrafficState
from shared.schemas.signal_plan import SignalPlan
from simulation.core.mock_simulation import MockTrafficSimulation
from simulation.scenarios.scenario_manager import load_scenario, list_scenarios


def test_scenario_manager_listing():
    scenarios = list_scenarios()
    assert "normal" in scenarios
    assert "heavy_traffic" in scenarios
    assert "emergency" in scenarios
    assert "road_closure" in scenarios


def test_scenario_manager_paths():
    for sc in list_scenarios():
        path = load_scenario(sc)
        assert path.endswith(".rou.xml")


def test_mock_simulation_lifecycle():
    sim = MockTrafficSimulation(scenario="normal")
    assert not sim.is_running
    sim.start()
    assert sim.is_running
    sim.step(5)
    assert sim.sim_time == 5.0
    sim.stop()
    assert not sim.is_running


def test_mock_traffic_state_schema_compliance():
    sim = MockTrafficSimulation(scenario="normal")
    sim.start()
    sim.step(10)
    state = sim.get_traffic_state()
    sim.stop()

    # Validate with Pydantic model directly
    validated = TrafficState.model_validate(state)
    assert validated.simulation_time == 10.0

    # Verify 4 junctions
    assert set(state["junctions"].keys()) == set(JUNCTION_IDS)
    for j_id, j_data in state["junctions"].items():
        assert "queue_ns" in j_data
        assert "queue_ew" in j_data
        assert "density" in j_data
        assert "avg_speed" in j_data
        assert "waiting_time" in j_data
        assert "throughput" in j_data
        assert "signal" in j_data
        assert "pedestrian_waiting" in j_data
        assert 0.0 <= j_data["density"] <= 1.0

    # Verify edges
    for edge_id in NETWORK_EDGES:
        assert edge_id in state["edges"]
        edge = state["edges"][edge_id]
        assert "vehicle_count" in edge
        assert "queue_length" in edge
        assert "density" in edge
        assert "average_speed" in edge
        assert "capacity" in edge
        assert edge["status"] == "OPEN"

    # Verify global
    g = state["global"]
    assert "vehicle_count" in g
    assert "average_speed" in g
    assert "average_waiting_time" in g
    assert "total_queue" in g
    assert "throughput" in g


def test_mock_signal_plan_application():
    sim = MockTrafficSimulation()
    sim.start()
    plan = {
        "signal_plan": {
            "J1": {"NS_green": 50.0, "EW_green": 10.0},
            "J2": {"NS_green": 15.0, "EW_green": 45.0},
        }
    }
    # Validate schema
    SignalPlan.model_validate(plan)

    sim.apply_signal_plan(plan)
    assert sim.signal_timings["J1"]["NS_green"] == 50.0
    assert sim.signal_timings["J1"]["EW_green"] == 10.0
    sim.stop()


def test_mock_edge_closure_and_reopen():
    sim = MockTrafficSimulation()
    sim.start()
    sim.step(5)

    sim.close_edge("J1_J2")
    state = sim.get_edge_state("J1_J2")
    assert state["status"] == "CLOSED"
    assert state["density"] == 0.0
    assert state["average_speed"] == 0.0

    sim.open_edge("J1_J2")
    reopened_state = sim.get_edge_state("J1_J2")
    assert reopened_state["status"] == "OPEN"
    sim.stop()


def test_mock_emergency_vehicle_injection():
    sim = MockTrafficSimulation()
    sim.start()
    v_id = sim.add_emergency_vehicle(["W1_J1", "J1_J2", "J2_E1"])
    assert v_id.startswith("mock_ambulance_")
    assert len(sim.emergency_vehicles) == 1
    sim.stop()


def test_mock_metrics_summary():
    sim = MockTrafficSimulation()
    sim.start()
    sim.step(20)
    metrics = sim.get_metrics()
    assert metrics["total_steps"] == 20
    assert "average_speed_kmh" in metrics
    assert "average_queue_length" in metrics
    assert "average_waiting_time_s" in metrics
    assert "total_travel_time_s" in metrics
    assert "total_fuel_consumption_ml" in metrics
    assert "total_co2_emissions_g" in metrics
    sim.stop()
