from pydantic import BaseModel, Field
from typing import List, Optional, Union

class Edge(BaseModel):
    from_node: str = Field(..., alias="from") # ТЗ использует зарезервированное слово 'from'
    to: str
    distance: float = Field(..., gt=0)

    class Config:
        populate_by_name = True

class GravityAssist(BaseModel):
    velocity_gain: float = Field(..., ge=0)
    fuel_consumption: float = Field(..., ge=0)
    time_to_execute: int = Field(..., ge=0)

class CelestialBody(BaseModel):
    id: str
    gravity_assists: List[GravityAssist]

class MissionData(BaseModel):
    total_fuel: float = Field(..., ge=0)
    mass_shuttle: float = Field(..., gt=0)
    mass_fuel_unit: float = Field(..., gt=0)
    power_per_unit: float = Field(..., gt=0)
    fuel_consumption: float = Field(..., ge=0)
    oxygen_time: int = Field(..., gt=0)
    edges: List[Edge]
    bodies: List[CelestialBody]

class MissionResponse(BaseModel):
    can_reach: bool
    min_flight_time: Optional[float] = None
    route: Optional[List[str]] = None
