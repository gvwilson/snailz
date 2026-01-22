"""Samples."""

from datetime import date
from pydantic import BaseModel, Field
import random
from typing import ClassVar

from .grid import grid_lat_lon
from . import utils


class Sample(BaseModel):
    """Represent a single sample."""

    id_stem: ClassVar[str] = "S"
    id_digits: ClassVar[int] = 4

    sample_id: str = Field(min_length=1, description="unique ID")
    grid_id: str = Field(min_length=1, description="grid ID")
    x_: int = Field(ge=0, description="X coordinate")
    y_: int = Field(ge=0, description="Y coordinate")
    lat: float = Field(description="latitude")
    lon: float = Field(description="longitude")
    pollution: int = Field(ge=0, description="pollution reading at grid cell")
    person_id: str = Field(description="collector")
    timestamp: date = Field(description="when sample was collected")
    mass: float = Field(gt=0.0, description="sample mass")

    @staticmethod
    def make(params, grids, persons):
        """Make a sample."""

        utils.ensure_id_generator(Sample)
        result = []
        for _ in range(params.num_samples):
            grid = random.choice(grids)
            x = random.randint(0, grid.size - 1)
            y = random.randint(0, grid.size - 1)
            lat, lon = grid_lat_lon(params, grid, x, y)
            pollution = grid[x, y]
            person = random.choice(persons)
            timestamp = utils.random_date(params)
            mass = utils.random_mass(params)
            result.append(
                Sample(
                    sample_id=next(Sample._id_gen),
                    grid_id=grid.grid_id,
                    x_=x,
                    y_=y,
                    lat=lat,
                    lon=lon,
                    pollution=pollution,
                    person_id=person.person_id,
                    timestamp=timestamp,
                    mass=mass,
                )
            )

        return result
