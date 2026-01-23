"""Samples."""

from datetime import date
from pydantic import BaseModel, ConfigDict, Field
import random
from typing import ClassVar

from . import utils


class Sample(BaseModel):
    """Represent a single sample."""

    id_stem: ClassVar[str] = "S"
    id_digits: ClassVar[int] = 4

    model_config = ConfigDict(
        json_schema_extra={
            "foreign_key": {
                "grid_id": ("grid", "grid_id"),
                "person_id": ("person", "person_id"),
            }
        }
    )

    sample_id: str = Field(
        min_length=1, description="unique ID", json_schema_extra={"primary_key": True}
    )
    grid_id: str = Field(min_length=1, description="grid ID")
    x: int = Field(default=0, ge=0, description="X coordinate")
    y: int = Field(default=0, ge=0, description="Y coordinate")
    person_id: str = Field(description="collector")
    timestamp: date = Field(description="when sample was collected")
    mass: float = Field(gt=0.0, description="sample mass")
    diameter: float = Field(gt=0.0, description="sample diameter")

    @staticmethod
    def make(params, grids, persons):
        """Make a sample."""

        utils.ensure_id_generator(Sample)
        result = []
        for _ in range(params.num_samples):
            grid = random.choice(grids)
            x = random.randint(0, grid.size - 1)
            y = random.randint(0, grid.size - 1)
            person = random.choice(persons)
            timestamp = utils.random_date(params)
            mass, diameter = utils.random_size(params)
            result.append(
                Sample(
                    sample_id=next(Sample._id_gen),
                    grid_id=grid.grid_id,
                    x=x,
                    y=y,
                    person_id=person.person_id,
                    timestamp=timestamp,
                    mass=mass,
                    diameter=diameter,
                )
            )

        return result
