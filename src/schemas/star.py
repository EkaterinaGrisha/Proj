from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class Vector2D(BaseModel):
    x: float
    y: float

    @model_validator(mode="after")
    def validate_not_zero(self) -> "Vector2D":
        if self.x == 0 and self.y == 0:
            raise ValueError("vector must be non-zero")
        return self


class CelestialBodyStar(BaseModel):
    type: Literal["star", "planet", "moon"]
    id: str
    radius: float = Field(..., gt=0)

    # Orbital parameters
    parent_id: Optional[str] = None
    orbit_radius: Optional[float] = Field(None, gt=0)
    angular_velocity: Optional[float] = Field(None, gt=0)
    initial_angle: Optional[float] = Field(None, ge=0, lt=360)
    rotation_clockwise: Optional[bool] = None

    # Static star parameters
    position: Optional[Vector2D] = None

    @model_validator(mode="after")
    def validate_body_type(self) -> "CelestialBodyStar":
        if self.type == "star":
            if self.position is None:
                raise ValueError(f"Star {self.id} must have position")
        else:
            fields = [self.parent_id, self.orbit_radius, self.angular_velocity, self.initial_angle, self.rotation_clockwise]
            if any(field is None for field in fields):
                raise ValueError(f"{self.type} {self.id} missing orbital data")
        return self


class ObservationParams(BaseModel):
    start_time: datetime
    required_transmission_time: int = Field(..., ge=1, le=10**6)


class StarVisibilityRequest(BaseModel):
    target_star_vector: Vector2D
    celestial_bodies: List[CelestialBodyStar] = Field(default_factory=list, max_length=100)
    observation_params: ObservationParams

    @field_validator("celestial_bodies")
    @classmethod
    def check_hierarchy(cls, bodies: List[CelestialBodyStar]) -> List[CelestialBodyStar]:
        ids = [body.id for body in bodies]
        if len(set(ids)) != len(ids):
            raise ValueError("body ids must be unique")

        id_map = {body.id: body for body in bodies}

        for body in bodies:
            if body.parent_id is None:
                continue

            if body.parent_id == "Atlas":
                if body.type != "moon":
                    raise ValueError("only moons can orbit Atlas")
                continue

            parent = id_map.get(body.parent_id)
            if parent is None:
                raise ValueError(f"Parent {body.parent_id} not found for {body.id}")

            if body.type == "planet" and parent.type != "star":
                raise ValueError(f"Planet {body.id} must orbit a star")
            if body.type == "moon" and parent.type != "planet":
                raise ValueError(f"Moon {body.id} must orbit a planet or Atlas")

        return bodies


class StarVisibilityResponse(BaseModel):
    found: bool
    next_fitting_interval_in: Optional[int] = None
    interval_duration: Optional[Union[int, str]] = None
