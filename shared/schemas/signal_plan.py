from typing import Dict, Optional
from pydantic import BaseModel, Field


class JunctionSignalPlan(BaseModel):
    """Green phase durations in seconds for a 2-stage (NS / EW) traffic signal."""
    NS_green: float = Field(..., gt=0.0, description="Green phase duration for North-South movements (seconds)")
    EW_green: float = Field(..., gt=0.0, description="Green phase duration for East-West movements (seconds)")
    yellow_time: float = Field(default=3.0, ge=1.0, description="Yellow transition clearance duration (seconds)")
    all_red_time: float = Field(default=1.0, ge=0.0, description="All-red safety clearance duration (seconds)")


class SignalPlan(BaseModel):
    """Signal timing optimization plan produced by Member 2 (QUBO / QAOA)."""
    signal_plan: Dict[str, JunctionSignalPlan] = Field(
        ...,
        description="Dictionary mapping junction IDs (e.g. 'J1', 'J2') to their green phase allocations"
    )
