import networkx as nx
from typing import List, Dict, Any

from .closure_manager import ClosureManager
from .accident_manager import AccidentManager

class EmergencyRoutePlanner:
    """Graph-based routing for emergency vehicles."""
    
    def __init__(self, closure_manager: ClosureManager, accident_manager: AccidentManager):
        self.graph = nx.DiGraph()
        self.closure_manager = closure_manager
        self.accident_manager = accident_manager

    def build_graph(self, edges_data: Dict[str, Any]) -> None:
        """
        Build NetworkX graph from traffic state edges.
        edges_data: dict mapping edge_id (e.g. 'J1_J2') to its attributes.
        """
        self.graph.clear()
        for edge_id, attrs in edges_data.items():
            # Parse source and target from edge_id assuming format "SRC_DEST"
            parts = edge_id.split('_')
            if len(parts) >= 2:
                u, v = parts[0], parts[1]
                
                # Base travel time = distance / speed or simplified to average_speed if distance unknown
                # Let's assume edge cost is loosely correlated with density/queue for now
                # Or just basic travel time if available
                avg_speed = max(attrs.get("average_speed", 10.0), 1.0) # avoid div by zero
                # assuming edge length is ~100m if not provided
                length = attrs.get("length", 100.0) 
                base_time = length / avg_speed
                
                self.graph.add_edge(u, v, edge_id=edge_id, base_time=base_time)

    def calculate_cost(self, u: str, v: str, edge_data: dict) -> float:
        """Calculate dynamic cost considering closures and accidents."""
        edge_id = edge_data['edge_id']
        
        if self.closure_manager.is_closed(edge_id):
            return float('inf')
            
        base_time = edge_data['base_time']
        
        # Check accident capacity reduction (which acts as a penalty)
        capacity_factor = 1.0
        if edge_id in self.accident_manager.active_accidents:
            capacity_factor = self.accident_manager.active_accidents[edge_id]
            
        # Cost increases inversely proportional to remaining capacity
        cost = base_time / max(capacity_factor, 0.01)
        return cost

    def find_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """Find the shortest emergency route."""
        if not self.graph.has_node(origin) or not self.graph.has_node(destination):
            return {"valid": False, "reason": "Origin or destination not in graph."}

        try:
            route = nx.shortest_path(
                self.graph, 
                source=origin, 
                target=destination, 
                weight=lambda u, v, d: self.calculate_cost(u, v, d)
            )
            
            # Calculate total estimated travel time
            travel_time = 0.0
            for i in range(len(route) - 1):
                u, v = route[i], route[i+1]
                edge_data = self.graph[u][v]
                travel_time += self.calculate_cost(u, v, edge_data)
                
            return {
                "valid": True,
                "route": route,
                "estimated_travel_time": travel_time
            }
        except nx.NetworkXNoPath:
            return {"valid": False, "reason": "No valid route found due to closures."}
