from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Union, Literal
from datetime import datetime

class Vector2D(BaseModel):
    x: float
    y: float

class CelestialBodyStar(BaseModel):
    type: Literal["star", "planet", "moon"]
    id: str
    radius: float = Field(..., gt=0)
    # Орбитальные параметры
    parent_id: Optional[str] = None
    orbit_radius: Optional[float] = Field(None, gt=0)
    angular_velocity: Optional[float] = Field(None, gt=0)
    initial_angle: Optional[float] = Field(None, ge=0, lt=360)
    rotation_clockwise: Optional[bool] = None
    # Параметры для звезд
    position: Optional[Vector2D] = None

    @model_validator(mode='after')
    def validate_body_type(self) -> 'CelestialBodyStar':
        if self.type == "star" and self.position is None:
            raise ValueError(f"Star {self.id} must have position")
        if self.type in ["planet", "moon"]:
            fields = [self.parent_id, self.orbit_radius, self.angular_velocity, self.initial_angle]
            if any(f is None for f in fields):
                raise ValueError(f"{self.type} {self.id} missing orbital data")
        return self

class ObservationParams(BaseModel):
    start_time: datetime
    required_transmission_time: int = Field(..., ge=1, le=10**6)

class StarVisibilityRequest(BaseModel):
    target_star_vector: Vector2D
    celestial_bodies: List[CelestialBodyStar]
    observation_params: ObservationParams

    @field_validator('celestial_bodies')
    @classmethod
    def check_hierarchy(cls, v: List[CelestialBodyStar]):
        ids = {b.id for b in v} | {"Atlas"}
        for b in v:
            if b.parent_id and b.parent_id not in ids:
                raise ValueError(f"Parent {b.parent_id} not found for {b.id}")
        return v

class StarVisibilityResponse(BaseModel):
    found: bool
    next_fitting_interval_in: Optional[int] = None
    # Union[int, str] позволяет вернуть "inf" как строку
    interval_duration: Optional[Union[int, str]] = None
