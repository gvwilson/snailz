"""Generate random grids."""

from collections import defaultdict
import io
import math
import random

from pydantic import BaseModel, Field

from . import utils


class GridParams(BaseModel):
    """Parameters for grid generation."""

    limit: float = Field(default=10.0, gt=0.0, description="Maximum pollution level")
    number: int = Field(default=3, gt=0, description="Number of grids")
    size: int = Field(default=15, gt=0, description="Grid size")

    model_config = {"extra": "forbid"}


class Grid(BaseModel):
    """A single grid."""

    ident: str = Field(description="grid identifier")
    cells: list[list] = Field(description="grid cells")
    size: int = Field(description="grid size")

    model_config = {"extra": "forbid"}

    def to_csv(self):
        """Create a CSV representation of a single grid.

        Returns:
            A CSV-formatted string with grid cells.
        """
        output = io.StringIO()
        for y in range(self.size - 1, -1, -1):
            temp = [f"{self.cells[x][y]}" for x in range(self.size)]
            print(",".join(temp), file=output)
        return output.getvalue()


class GridList(BaseModel):
    """A set of generated grids."""

    model_config = {"extra": "forbid"}

    grids: list[Grid] = Field(description="all grids")


def grids_generate(parameters):
    """Generate random grids."""

    gen = utils.UniqueIdGenerator("grid", _grid_id_generator)
    grids = []
    for _ in range(parameters.number):
        grids.append(_make_grid(parameters, gen.next()))
    return GridList(grids=grids)


def _grid_id_generator():
    """Generate unique ID for a grid (CNNN)."""

    num = random.randint(0, 999)
    return f"G{num:03d}"


def _make_grid(params, ident):
    """Create a grid of specified size and fill with random values."""

    cells = [[0.0 for _ in range(params.size)] for _ in range(params.size)]
    center = params.size // 2
    cells[center][center] = random.uniform(params.limit / 2, params.limit)

    radial_groups = _make_radial_groups(params.size)
    for inv_dist in sorted(radial_groups.keys()):
        points = radial_groups[inv_dist]
        temp = []
        for (x, y) in points:
            temp.append((x, y, _make_value(cells, x, y, params.limit, inv_dist)))
        for (x, y, val) in temp:
            cells[x][y] = val

    return Grid(ident=ident, size=params.size, cells=cells)


def _make_radial_groups(size):
    """Group points by distance from center."""
    groups = defaultdict(set)
    center = size // 2
    for x in range(size):
        for y in range(size):
            if (x == center) and (y == center):
                continue
            inv_dist = center - math.sqrt((x - center) ** 2 + (y - center) ** 2) / size
            groups[inv_dist].add((x, y))
    return groups


def _make_value(cells, x, y, limit, inv_dist):
    """Generate a single cell value."""

    cutoff = limit * inv_dist
    return random.uniform(cutoff / 2, cutoff)
