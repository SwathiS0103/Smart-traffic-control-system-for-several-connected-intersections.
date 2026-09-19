import json
import os
import sys

# Add src to python path
sys.path.insert(0, os.path.dirname(__file__))

from src.event_engine import EventEngine
from src.event_models import Event, EventType, EventSeverity, EmergencyVehicle
from src.congestion_detector import CongestionDetector
from src.accident_manager import AccidentManager
from src.closure_manager import ClosureManager
from src.emergency_route import EmergencyRoutePlanner
from src.green_corridor import GreenCorridorManager
from src.priority_manager import PriorityManager
from src.impact_analyzer import ImpactAnalyzer
from src.rerouting import ReroutingManager
from src.weight_manager import WeightManager
from src.integration_adapter import IntegrationAdapter

def run_demo():
    print("==================================================")
    print(" Q-FLOW Dynamic Event Management Demonstration ")
    print("==================================================")
    
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'event_config.yaml')
    state_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_traffic_state.json')
    
    with open(state_path, 'r') as f:
        traffic_state = json.load(f)
        
    print("\n[INFO] Loaded traffic state.")
    
    # Initialize components
    engine = EventEngine()
    congestion_det = CongestionDetector(config_path)
    accident_mgr = AccidentManager()
    closure_mgr = ClosureManager()
    
    route_planner = EmergencyRoutePlanner(closure_mgr, accident_mgr)
    route_planner.build_graph(traffic_state.get('edges', {}))
    
    green_corridor_mgr = GreenCorridorManager(route_planner, config_path)
    priority_mgr = PriorityManager(config_path)
    impact_analyzer = ImpactAnalyzer(config_path)
    rerouting_mgr = ReroutingManager(route_planner)
    weight_mgr = WeightManager()

    # SCENARIO 1: NORMAL TRAFFIC
    print("\n=== SCENARIO 1: NORMAL TRAFFIC ===")
    weights = weight_mgr.calculate_weights(engine.get_active_events())
    print("Optimizer Weights:", weights)
    
    # SCENARIO 2: SUDDEN CONGESTION
    print("\n=== SCENARIO 2: SUDDEN CONGESTION ===")
    # Pretend J2 density jumped to 0.82
    traffic_state["junctions"]["J2"]["density"] = 0.82
    congestion_res = congestion_det.detect_congestion(traffic_state)
    if congestion_res["J2"]["congestion_level"] == "CRITICAL":
        print("Detected CRITICAL congestion at J2")
        e = Event(event_id="E001", type=EventType.CONGESTION, location="J2", severity=EventSeverity.CRITICAL, start_time=120)
        engine.add_event(e)
        engine.activate_event("E001")
        
    # SCENARIO 3 & 4: ACCIDENT & CLOSURE
    print("\n=== SCENARIO 3 & 4: ACCIDENT & ROAD CLOSURE ===")
    print("Accident reported on J2_J3. Road closed.")
    accident_mgr.create_accident("J2_J3", EventSeverity.HIGH)
    closure_mgr.add_closure("J2_J3")
    e2 = Event(event_id="E002", type=EventType.ROAD_CLOSURE, location="J2_J3", severity=EventSeverity.HIGH, start_time=125)
    engine.add_event(e2)
    engine.activate_event("E002")
    
    impact = impact_analyzer.analyze_impact(e2, route_planner.graph)
    print("Impact Analysis:", impact)
    
    weights = weight_mgr.calculate_weights(engine.get_active_events())
    print("Optimizer Weights (Adjusted for Closure):", weights)

    # SCENARIO 5 & 7: AMBULANCE + ROUTING AROUND CLOSURE
    print("\n=== SCENARIO 5 & 7: EMERGENCY REROUTING ===")
    amb = EmergencyVehicle(vehicle_id="AMB001", type="AMBULANCE", origin="J1", destination="J6", route=["J1", "J2", "J3", "J6"])
    
    print(f"Original Route: {amb.route}")
    # Reroute because J2_J3 is closed
    reroute_res = rerouting_mgr.calculate_alternative_route(amb.origin, amb.destination, amb.route)
    if reroute_res["success"]:
        amb.route = reroute_res["alternative_route"]
        print(f"Rerouted to avoid closure: {amb.route}")
        print(f"Estimated Travel Time: {reroute_res['additional_time']}")
        
    corridor = green_corridor_mgr.generate_corridor(amb.vehicle_id, amb.route, current_time=130)
    print("Green Corridor generated:", json.dumps(corridor, indent=2))
    
    valid = priority_mgr.validate_corridor(corridor, current_time=130)
    print(f"Corridor Safety Check: {'PASSED' if valid['valid'] else 'FAILED'}")

    e3 = Event(event_id="E003", type=EventType.EMERGENCY, location="AMB001", severity=EventSeverity.CRITICAL, start_time=130)
    engine.add_event(e3)
    engine.activate_event("E003")

    # Final Integration Request
    print("\n=== OPTIMIZER REQUEST GENERATION ===")
    weights = weight_mgr.calculate_weights(engine.get_active_events())
    print("Optimizer Weights (Emergency overrides):", weights)
    
    req = IntegrationAdapter.build_optimizer_request(
        traffic_state=traffic_state,
        active_events=engine.get_active_events(),
        weights=weights,
        active_emergencies=[amb],
        green_corridors={amb.vehicle_id: corridor}
    )
    
    # Save output for proof
    out_path = os.path.join(os.path.dirname(__file__), 'data', 'optimizer_request.json')
    with open(out_path, 'w') as f:
        json.dump(req, f, indent=2)
        
    print(f"[SUCCESS] Optimizer Request JSON written to {out_path}")

if __name__ == "__main__":
    run_demo()
