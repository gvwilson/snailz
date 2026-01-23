"""Sample grids."""

import math
from pydantic import BaseModel, Field
import random
from typing import ClassVar

from . import utils


# Convert lat/lon to distances.
METERS_PER_DEGREE_LAT = 111_320.0

# Legal moves for random walk that fills grid.
MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]]


class Grid(BaseModel):
    """Create and fill an integer grid."""

    id_stem: ClassVar[str] = "G"
    id_digits: ClassVar[int] = 4

    grid_id: str = Field(
        min_length=1, description="unique ID", json_schema_extra={"primary_key": True}
    )
    size: int = Field(gt=0, description="grid size")
    grid: list = Field(default_factory=list, description="grid values")
    lat0: float = Field(default=0.0, description="southernmost latitude")
    lon0: float = Field(default=0.0, description="westernmost longitude")

    @staticmethod
    def make(params):
        """Make grids."""

        utils.ensure_id_generator(Grid)
        origins = _grid_origins(params)
        result = []
        for lat0, lon0 in origins:
            grid = Grid(
                grid_id=next(Grid._id_gen), size=params.grid_size, lat0=lat0, lon0=lon0
            )
            grid.fill()
            result.append(grid)
        return result

    @staticmethod
    def tidy(params, grids):
        """Convert all grids to tidy table."""

        result = [["grid_id", "x", "y", "lat", "lon", "pollution"]]
        for g in grids:
            for x in range(g.size):
                for y in range(g.size):
                    if g[x, y] > 0:
                        lat, lon = grid_lat_lon(params, g, x, y)
                        result.append([g.grid_id, x, y, lat, lon, g[x, y]])
        return result

    def __getitem__(self, key):
        """Get grid element."""

        x, y = key
        return self.grid[y * self.size + x]

    def __setitem__(self, key, value):
        """Set grid element."""

        x, y = key
        self.grid[y * self.size + x] = value

    def __str__(self):
        """Convert to CSV string."""

        result = []
        for y in range(self.size - 1, -1, -1):
            result.append(",".join([str(self[x, y]) for x in range(self.size)]))
        return "\n".join(result)

    def fill(self):
        """Fill in a grid."""

        center = self.size // 2
        size_1 = self.size - 1
        x, y = center, center

        self.grid = [0 for _ in range(self.size * self.size)]
        while (x != 0) and (y != 0) and (x != size_1) and (y != size_1):
            self[x, y] += 1
            m = random.choice(MOVES)
            x += m[0]
            y += m[1]


def grid_lat_lon(params, grid, x, y):
    """Calculate latitude and longitude of grid cell."""

    lat = grid.lat0 + (y * params.grid_spacing) / METERS_PER_DEGREE_LAT
    meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(grid.lat0))
    lon = grid.lon0 + (x * params.grid_spacing) / meters_per_degree_lon
    return lat, lon


def _grid_origins(params):
    """
    Generate non-overlapping lower-left (lat, lon) corners for grids.
    """

    grid_width_m = params.grid_size * params.grid_spacing
    stride_m = grid_width_m + params.grid_gap
    cols = math.ceil(math.sqrt(params.num_grids))
    meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(params.lat0))

    origins = []
    for i in range(params.num_grids):
        dx = (i % cols) * stride_m
        dy = (i // cols) * stride_m
        origins.append(
            (
                params.lat0 + dy / METERS_PER_DEGREE_LAT,
                params.lon0 + dx / meters_per_degree_lon,
            )
        )

    return origins
