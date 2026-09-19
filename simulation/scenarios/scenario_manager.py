"""Scenario management for Q-FLOW simulation.
Provides standard scenarios: normal, heavy_traffic, emergency, road_closure.
"""

from pathlib import Path
from typing import List, Dict

SCENARIO_DIR = Path(__file__).resolve().parent

SCENARIO_FILES: Dict[str, str] = {
    "normal": "normal.rou.xml",
    "heavy_traffic": "heavy_traffic.rou.xml",
    "emergency": "emergency.rou.xml",
    "road_closure": "road_closure.rou.xml",
}


def list_scenarios() -> List[str]:
    """Return list of available scenario identifiers."""
    return list(SCENARIO_FILES.keys())


def load_scenario(name: str) -> str:
    """Return the absolute path to the requested scenario's route file.

    Args:
        name: One of 'normal', 'heavy_traffic', 'emergency', 'road_closure'

    Returns:
        Absolute string path to the route XML file.

    Raises:
        ValueError: If the scenario name is unknown.
        FileNotFoundError: If the scenario XML file is missing.
    """
    clean_name = name.strip().lower()
    if clean_name not in SCENARIO_FILES:
        raise ValueError(
            f"Unknown scenario '{name}'. Available scenarios: {list_scenarios()}"
        )

    file_path = SCENARIO_DIR / SCENARIO_FILES[clean_name]
    if not file_path.exists():
        raise FileNotFoundError(f"Scenario route file not found at: {file_path}")

    return str(file_path)
