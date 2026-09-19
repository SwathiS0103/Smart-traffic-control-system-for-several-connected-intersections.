from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class JunctionState(BaseModel):
    """Telemetry and operational state of a single traffic intersection."""
    queue_ns: int = Field(default=0, description="Number of halting vehicles on North-South approaches")
    queue_ew: int = Field(default=0, description="Number of halting vehicles on East-West approaches")
    density: float = Field(default=0.0, ge=0.0, le=1.0, description="Normalized vehicle density across approaches [0.0 - 1.0]")
    avg_speed: float = Field(default=0.0, ge=0.0, description="Average speed of vehicles in approach zones (km/h)")
    waiting_time: float = Field(default=0.0, ge=0.0, description="Average waiting time of vehicles at this junction (s)")
    throughput: int = Field(default=0, ge=0, description="Total vehicles that have cleared this intersection")
    signal: str = Field(default="NS_GREEN", description="Current active signal phase ('NS_GREEN', 'EW_GREEN', 'YELLOW', etc.)")
    pedestrian_waiting: int = Field(default=0, ge=0, description="Number of pedestrians waiting at crossings")


class EdgeState(BaseModel):
    """Telemetry and operational state of an edge (road segment)."""
    vehicle_count: int = Field(default=0, ge=0, description="Current number of active vehicles on the edge")
    queue_length: int = Field(default=0, ge=0, description="Number of queuing / halting vehicles on the edge")
    density: float = Field(default=0.0, ge=0.0, le=1.0, description="Vehicle count divided by road capacity [0.0 - 1.0]")
    average_speed: float = Field(default=0.0, ge=0.0, description="Mean speed of active vehicles on the edge (km/h)")
    capacity: int = Field(default=60, gt=0, description="Theoretical maximum vehicle holding capacity")
    status: Literal["OPEN", "CLOSED"] = Field(default="OPEN", description="Operational status of the road")


class GlobalTrafficState(BaseModel):
    """System-wide aggregate traffic metrics across all junctions and edges."""
    vehicle_count: int = Field(default=0, ge=0, description="Total active vehicles in the entire network")
    average_speed: float = Field(default=0.0, ge=0.0, description="Network-wide mean vehicle speed (km/h)")
    average_waiting_time: float = Field(default=0.0, ge=0.0, description="Network-wide average waiting time (s)")
    total_queue: int = Field(default=0, ge=0, description="Total halting vehicles across all approaches")
    throughput: int = Field(default=0, ge=0, description="Total vehicles that have arrived at their destination")
    total_travel_time: float = Field(default=0.0, ge=0.0, description="Cumulative travel time of all completed trips (s)")
    fuel_consumption_ml: float = Field(default=0.0, ge=0.0, description="Estimated total fuel consumption (milliliters)")
    co2_emissions_g: float = Field(default=0.0, ge=0.0, description="Estimated total CO2 emissions (grams)")


class TrafficState(BaseModel):
    """Root data contract for traffic digital twin telemetry."""
    timestamp: float = Field(..., description="UNIX timestamp or epoch reference")
    simulation_time: float = Field(..., ge=0.0, description="Current SUMO simulation elapsed time in seconds")
    junctions: Dict[str, JunctionState] = Field(default_factory=dict, description="Per-junction telemetry keyed by junction ID")
    edges: Dict[str, EdgeState] = Field(default_factory=dict, description="Per-edge telemetry keyed by edge ID")
    global_metrics: GlobalTrafficState = Field(..., alias="global", description="Global network aggregates")

    model_config = ConfigDict(populate_by_name=True)
