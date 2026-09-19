import yaml
import os
from typing import Dict, Any, Optional

class CongestionDetector:
    """Detects congestion levels dynamically from traffic state."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        # Default thresholds in case config is missing
        self.thresholds = self.config.get("congestion", {
            "low_density": 0.30,
            "medium_density": 0.60,
            "high_density": 0.80
        })

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def detect_congestion(self, traffic_state: Dict[str, Any]) -> Dict[str, dict]:
        """
        Evaluate traffic state and return a dict mapping junction_id to congestion info.
        """
        results = {}
        junctions = traffic_state.get("junctions", {})
        
        for j_id, data in junctions.items():
            density = data.get("density", 0.0)
            queue = data.get("queue_ns", 0) + data.get("queue_ew", 0)
            avg_speed = data.get("avg_speed", 0.0)
            
            level = self._evaluate_level(density)
            
            results[j_id] = {
                "junction": j_id,
                "congestion_level": level,
                "density": density,
                "queue": queue,
                "avg_speed": avg_speed
            }
            
        return results

    def _evaluate_level(self, density: float) -> str:
        if density < self.thresholds.get("low_density", 0.30):
            return "LOW"
        elif density < self.thresholds.get("medium_density", 0.60):
            return "MEDIUM"
        elif density < self.thresholds.get("high_density", 0.80):
            return "HIGH"
        else:
            return "CRITICAL"
