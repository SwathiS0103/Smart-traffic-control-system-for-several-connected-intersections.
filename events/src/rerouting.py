from typing import Dict, List, Any
from .emergency_route import EmergencyRoutePlanner

class ReroutingManager:
    """Calculates alternative routes during road closures or severe congestion."""
    
    def __init__(self, route_planner: EmergencyRoutePlanner):
        self.route_planner = route_planner

    def calculate_alternative_route(self, origin: str, destination: str, original_route: List[str]) -> Dict[str, Any]:
        """Find an alternative route and compare with the original."""
        
        # Original travel time estimate (without closures/accidents)
        # For simplicity, we just calculate the cost of the original route under CURRENT conditions.
        # If it's infinite, it means it's closed.
        original_time = 0.0
        is_original_closed = False
        
        for i in range(len(original_route) - 1):
            u, v = original_route[i], original_route[i+1]
            if self.route_planner.graph.has_edge(u, v):
                edge_data = self.route_planner.graph[u][v]
                cost = self.route_planner.calculate_cost(u, v, edge_data)
                if cost == float('inf'):
                    is_original_closed = True
                original_time += cost
            else:
                original_time += 15.0 # fallback
                
        # Find new route
        new_route_result = self.route_planner.find_route(origin, destination)
        
        if not new_route_result["valid"]:
            return {
                "success": False,
                "reason": new_route_result["reason"]
            }
            
        new_route = new_route_result["route"]
        new_time = new_route_result["estimated_travel_time"]
        
        # If original route is closed, original time is effectively infinite.
        additional_time = new_time - original_time if not is_original_closed else -1.0
        
        return {
            "success": True,
            "original_route": original_route,
            "alternative_route": new_route,
            "additional_time": round(additional_time, 1),
            "original_closed": is_original_closed
        }
