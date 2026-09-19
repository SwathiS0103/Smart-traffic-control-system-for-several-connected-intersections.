import yaml
import os
from typing import Dict, Any

class PriorityManager:
    """Validates green corridors for safety constraints."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.min_green = self.config.get("emergency", {}).get("min_green", 10)
        self.max_green = self.config.get("emergency", {}).get("max_green", 60)
        self.clearance_time = self.config.get("emergency", {}).get("clearance_time", 5)

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def validate_corridor(self, corridor_plan: Dict[str, Any], current_time: float) -> Dict[str, Any]:
        """
        Ensure the green corridor is safe to execute.
        Checks min green, clearance times, etc.
        """
        for step in corridor_plan.get("corridor", []):
            green_start = step["green_start"]
            green_end = step["green_end"]
            
            # Check 1: Time paradox (can't start in the past)
            if green_start < current_time - 1.0: # 1s tolerance
                return {
                    "valid": False,
                    "reason": f"Corridor step at {step['junction']} scheduled in the past."
                }
                
            # Check 2: Minimum green time for safety (allow some crossing if needed)
            duration = green_end - green_start
            if duration < self.min_green:
                return {
                    "valid": False,
                    "reason": f"Insufficient green time allocated at {step['junction']}."
                }
                
            # Check 3: Clearance time buffer (must have enough time to clear intersection)
            if duration < self.clearance_time:
                return {
                    "valid": False,
                    "reason": f"INSUFFICIENT_CLEARANCE_TIME at {step['junction']}."
                }
                
        return {"valid": True}
