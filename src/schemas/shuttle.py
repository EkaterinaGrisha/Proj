from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_node: str = Field(..., alias="from") # ТЗ использует зарезервированное слово 'from'
    to: str
    distance: float = Field(..., gt=0)

class GravityAssist(BaseModel):
    model_config = ConfigDict(extra="forbid")

    velocity_gain: float = Field(..., ge=0)
    fuel_consumption: int = Field(..., ge=0)
    time_to_execute: int = Field(..., ge=0)

class CelestialBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    gravity_assists: List[GravityAssist]

class MissionData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_fuel: int = Field(..., ge=0)
    mass_shuttle: float = Field(..., gt=0)
    mass_fuel_unit: float = Field(..., gt=0)
    power_per_unit: float = Field(..., gt=0)
    fuel_consumption: float = Field(..., ge=0)
    oxygen_time: int = Field(..., gt=0)
    edges: List[Edge]
    bodies: List[CelestialBody]

    @model_validator(mode="after")
    def validate_consistency(self):
        if len(self.bodies) > 100:
            raise ValueError("len(bodies) must be <= 100")
        if not self.edges:
            raise ValueError("edges must not be empty")

        body_ids = [body.id for body in self.bodies]
        if len(set(body_ids)) != len(body_ids):
            raise ValueError("body ids must be unique")
        if "start_point" in body_ids or "rescue_point" in body_ids:
            raise ValueError("start_point/rescue_point must not be included into bodies")

        known_nodes = set(body_ids) | {"start_point", "rescue_point"}
        start_mentioned = False
        rescue_mentioned = False
        for edge in self.edges:
            if edge.from_node not in known_nodes or edge.to not in known_nodes:
                raise ValueError("edge references unknown body id")
            start_mentioned = start_mentioned or edge.from_node == "start_point" or edge.to == "start_point"
            rescue_mentioned = rescue_mentioned or edge.from_node == "rescue_point" or edge.to == "rescue_point"

        if not start_mentioned or not rescue_mentioned:
            raise ValueError("start_point and rescue_point must be present in edges")

        return self

class MissionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    can_reach: bool
    min_flight_time: Optional[float] = None
    route: Optional[List[str]] = None
