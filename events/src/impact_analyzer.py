import networkx as nx
from typing import Dict, List, Any
import yaml
import os

from .event_models import Event, EventSeverity

class ImpactAnalyzer:
    """Calculates blast-radius and impact of events on the network."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.radius = self.config.get("impact", {}).get("radius", 2)
        
    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def analyze_impact(self, event: Event, graph: nx.DiGraph) -> Dict[str, Any]:
        """Determine direct and secondary affected junctions."""
        direct = []
        
        # If location is an edge (e.g. J2_J3), direct is J2 and J3
        if "_" in event.location:
            parts = event.location.split("_")
            direct = [parts[0], parts[1]]
        else:
            direct = [event.location]
            
        secondary = set()
        
        for node in direct:
            if not graph.has_node(node):
                continue
                
            # Perform BFS/ego_graph to find neighbors within radius
            ego = nx.ego_graph(graph, node, radius=self.radius, undirected=True)
            for neighbor in ego.nodes:
                if neighbor not in direct:
                    secondary.add(neighbor)
                    
        return {
            "event_id": event.event_id,
            "impact": {
                "direct": direct,
                "secondary": list(secondary),
                "severity": event.severity.value,
                "radius": self.radius
            }
        }
