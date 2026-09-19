"""Simulation configuration and network topology constants for Q-FLOW.
"""

from typing import Dict, List

# 4-intersection grid junction IDs
JUNCTION_IDS = ["J1", "J2", "J3", "J4"]

# Mapping of junction IDs to their incoming edges categorized by orientation (NS vs EW)
JUNCTION_APPROACHES: Dict[str, Dict[str, List[str]]] = {
    "J1": {
        "NS": ["N1_J1", "J3_J1"],
        "EW": ["W1_J1", "J2_J1"],
    },
    "J2": {
        "NS": ["N2_J2", "J4_J2"],
        "EW": ["J1_J2", "E1_J2"],
    },
    "J3": {
        "NS": ["J1_J3", "S1_J3"],
        "EW": ["W2_J3", "J4_J3"],
    },
    "J4": {
        "NS": ["J2_J4", "S2_J4"],
        "EW": ["J3_J4", "E2_J4"],
    },
}

# All navigable edges in the 2x2 grid network
NETWORK_EDGES = [
    # Boundary inward / outward edges
    "N1_J1", "J1_N1",
    "N2_J2", "J2_N2",
    "S1_J3", "J3_S1",
    "S2_J4", "J4_S2",
    "W1_J1", "J1_W1",
    "W2_J3", "J3_W2",
    "E1_J2", "J2_E1",
    "E2_J4", "J4_E2",
    # Internal grid arterial edges
    "J1_J2", "J2_J1",
    "J3_J4", "J4_J3",
    "J1_J3", "J3_J1",
    "J2_J4", "J4_J2",
]

# Standard edge length in meters
GRID_BLOCK_LENGTH_M = 150.0

# Road capacities (length = 150m, 2 lanes per edge, avg vehicle space = 7.5m -> 40 vehicles)
DEFAULT_EDGE_CAPACITY = 40

# Speed limits (13.89 m/s ≈ 50 km/h)
DEFAULT_SPEED_LIMIT_MPS = 13.89

# Default signal timings in seconds
DEFAULT_NS_GREEN = 30.0
DEFAULT_EW_GREEN = 30.0
DEFAULT_YELLOW_TIME = 3.0
DEFAULT_ALL_RED_TIME = 1.0

# SUMO Phase indexing convention for standard 4-stage program:
# Phase 0: NS Green, EW Red
# Phase 1: NS Yellow, EW Red
# Phase 2: NS Red, EW Green
# Phase 3: NS Red, EW Yellow
PHASE_NS_GREEN = 0
PHASE_NS_YELLOW = 1
PHASE_EW_GREEN = 2
PHASE_EW_YELLOW = 3
