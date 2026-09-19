import yaml
import os
from typing import Dict, List, Any
from .emergency_route import EmergencyRoutePlanner

class GreenCorridorManager:
    """Calculates ETAs and generates a green corridor for emergency vehicles."""
    
    def __init__(self, route_planner: EmergencyRoutePlanner, config_path: str):
        self.route_planner = route_planner
        self.config_path = config_path
        self.config = self._load_config()
        self.eta_buffer = self.config.get("emergency", {}).get("eta_buffer", 5)

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def calculate_eta_for_route(self, route: List[str], current_time: float) -> List[Dict[str, Any]]:
        """Calculate ETA at each junction in the route."""
        etas = []
        cumulative_time = 0.0
        
        # Assume route is a list of node IDs (junctions)
        for i in range(len(route)):
            junction = route[i]
            
            # The first junction is the current location, ETA is 0 + current_time
            if i == 0:
                etas.append({
                    "junction": junction,
                    "eta": current_time,
                    "direction": "START" # Simplify direction for now
                })
                continue
                
            prev = route[i-1]
            if self.route_planner.graph.has_edge(prev, junction):
                edge_data = self.route_planner.graph[prev][junction]
                cost = self.route_planner.calculate_cost(prev, junction, edge_data)
                cumulative_time += cost
            else:
                # Fallback if edge data is missing
                cumulative_time += 15.0
                
            # Naive direction inference
            direction = f"{prev}_TO_{junction}"
                
            etas.append({
                "junction": junction,
                "eta": current_time + cumulative_time,
                "direction": direction
            })
            
        return etas

    def generate_corridor(self, vehicle_id: str, route: List[str], current_time: float) -> Dict[str, Any]:
        """Generate green corridor schedule based on ETAs."""
        etas = self.calculate_eta_for_route(route, current_time)
        
        corridor = []
        for stop in etas:
            # We want the light to be green slightly before arrival, and stay green slightly after
            green_start = stop["eta"] - self.eta_buffer
            # Default window of 15 seconds plus buffer
            green_end = stop["eta"] + 15 + self.eta_buffer
            
            corridor.append({
                "junction": stop["junction"],
                "eta": round(stop["eta"], 1),
                "direction": stop["direction"],
                "green_start": round(max(current_time, green_start), 1),
                "green_end": round(green_end, 1)
            })
            
        return {
            "vehicle_id": vehicle_id,
            "corridor": corridor
        }
