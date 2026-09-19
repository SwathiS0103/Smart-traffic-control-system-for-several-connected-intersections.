from typing import Set, Dict, Any

class ClosureManager:
    """Manages temporary road closures."""
    
    def __init__(self):
        self.closed_edges: Set[str] = set()

    def add_closure(self, edge_id: str) -> Dict[str, Any]:
        """Mark a road as closed."""
        self.closed_edges.add(edge_id)
        return {
            "edge": edge_id,
            "closed": True,
            "reason": "ROAD_CLOSURE"
        }

    def remove_closure(self, edge_id: str) -> None:
        """Reopen a road."""
        if edge_id in self.closed_edges:
            self.closed_edges.remove(edge_id)

    def is_closed(self, edge_id: str) -> bool:
        """Check if a road is closed."""
        return edge_id in self.closed_edges

    def get_closed_edges(self) -> Set[str]:
        """Return all currently closed edges."""
        return self.closed_edges.copy()
