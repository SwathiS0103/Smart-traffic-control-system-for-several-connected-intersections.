import json
import os
import random

class DemoManager:
    """Provides mock data for the dashboard when backend services are disconnected."""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        # In a real app, we would load from JSON files. For the hackathon speed, 
        # we can generate deterministic state here.
        
    def get_state_for_scenario(self, scenario: str, step: int) -> dict:
        # Base state
        data = {
            "sumo_connected": False,
            "quantum_ready": True,
            "event_ready": True,
            "time": f"{step // 60:02d}:{step % 60:02d}",
            "metrics": {
                "waiting_time": round(15.0 + (step * 0.1), 1),
                "queue_length": int(20 + (step * 0.5)),
                "throughput": int(800 - (step * 2)),
                "speed": round(30.0 - (step * 0.2), 1),
                "fuel": round(120.0 + (step * 0.5), 1),
                "co2": round(280.0 + (step * 1.2), 1),
                "emergency_time": 0
            },
            "events": [],
            "emergencies": [],
            "junctions": {
                "J1": {"density": 0.4, "queue": 10, "signal": "NS", "lat": 13.080, "lon": 80.270},
                "J2": {"density": 0.5, "queue": 15, "signal": "EW", "lat": 13.085, "lon": 80.275},
                "J3": {"density": 0.3, "queue": 5, "signal": "NS", "lat": 13.090, "lon": 80.270},
                "J4": {"density": 0.6, "queue": 20, "signal": "EW", "lat": 13.080, "lon": 80.280},
                "J5": {"density": 0.4, "queue": 12, "signal": "NS", "lat": 13.085, "lon": 80.285},
                "J6": {"density": 0.5, "queue": 18, "signal": "EW", "lat": 13.090, "lon": 80.280}
            },
            "edges": [
                {"id": "J1_J2", "status": "OPEN", "density": 0.4, "coords": [[13.080, 80.270], [13.085, 80.275]]},
                {"id": "J2_J3", "status": "OPEN", "density": 0.5, "coords": [[13.085, 80.275], [13.090, 80.270]]},
                {"id": "J1_J4", "status": "OPEN", "density": 0.3, "coords": [[13.080, 80.270], [13.080, 80.280]]},
                {"id": "J2_J5", "status": "OPEN", "density": 0.6, "coords": [[13.085, 80.275], [13.085, 80.285]]},
                {"id": "J4_J5", "status": "OPEN", "density": 0.4, "coords": [[13.080, 80.280], [13.085, 80.285]]},
                {"id": "J5_J6", "status": "OPEN", "density": 0.5, "coords": [[13.085, 80.285], [13.090, 80.280]]},
                {"id": "J3_J6", "status": "OPEN", "density": 0.3, "coords": [[13.090, 80.270], [13.090, 80.280]]}
            ],
            "quantum": {
                "method": "QAOA",
                "backend": "Qiskit Aer Simulator",
                "depth": 1,
                "shots": 1024,
                "variables": 12,
                "objective_value": 0.314,
                "execution_time": "145 ms",
                "best_bitstring": "101100101101",
                "top_strings": {"101100101101": 0.31, "101000101101": 0.21, "111100101101": 0.16}
            },
            "signal_comparison": {
                "J1": {"current": "NS 30", "classical": "NS 38", "qaoa": "NS 42"},
                "J2": {"current": "EW 40", "classical": "EW 35", "qaoa": "EW 45"},
                "J3": {"current": "NS 30", "classical": "NS 32", "qaoa": "NS 37"}
            },
            "performance_comparison": {
                "Fixed": {"waiting": 45.2, "queue": 35, "throughput": 720, "fuel": 150.0, "co2": 320.0},
                "Classical": {"waiting": 38.5, "queue": 28, "throughput": 810, "fuel": 135.0, "co2": 290.0},
                "QAOA": {"waiting": 34.2, "queue": 22, "throughput": 860, "fuel": 125.0, "co2": 275.0}
            }
        }
        
        # Apply Scenario specific modifiers
        if "Congestion" in scenario:
            data["junctions"]["J2"]["density"] = 0.85
            data["junctions"]["J2"]["queue"] = 45
            data["metrics"]["waiting_time"] += 20
            data["metrics"]["throughput"] -= 200
            data["events"].append({
                "time": data["time"],
                "event": "Heavy congestion at J2",
                "status": "ACTIVE",
                "type": "CONGESTION"
            })
            
        if "Accident" in scenario:
            data["junctions"]["J3"]["density"] = 0.95
            data["edges"][1]["status"] = "ACCIDENT"
            data["events"].append({
                "time": data["time"],
                "event": "Accident J2-J3",
                "status": "ACTIVE",
                "type": "ACCIDENT",
                "severity": "HIGH",
                "impact": {"direct": ["J2", "J3"], "secondary": ["J1", "J5"]}
            })
            
        if "Closure" in scenario:
            data["edges"][1]["status"] = "CLOSED"
            data["events"].append({
                "time": data["time"],
                "event": "Road Closure J2-J3",
                "status": "ACTIVE",
                "type": "ROAD_CLOSURE"
            })
            
        if "Emergency" in scenario:
            data["emergencies"].append({
                "vehicle_id": "AMB001",
                "origin": "J1",
                "destination": "J6",
                "eta": 61 - (step % 61),
                "route": ["J1", "J4", "J5", "J6"] if "Closure" in scenario else ["J1", "J2", "J3", "J6"],
                "status": "GREEN CORRIDOR ACTIVE",
                "corridor": [
                    {"junction": "J1", "eta": 12, "green_start": 7, "green_end": 27},
                    {"junction": "J4", "eta": 35, "green_start": 30, "green_end": 50},
                ]
            })
            data["metrics"]["emergency_time"] = 45 if "Closure" in scenario else 38
            
        return data
