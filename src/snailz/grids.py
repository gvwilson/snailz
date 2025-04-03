"""Generate random grids."""

from collections import defaultdict
import io
import math
import random

from pydantic import BaseModel, Field

from . import utils


class Point(BaseModel):
    """A 2D point with x and y coordinates."""

    x: int = Field(ge=0, description="x coordinate")
    y: int = Field(ge=0, description="y coordinate")


class GridParams(BaseModel):
    """Parameters for grid generation."""

    limit: float = Field(default=10.0, gt=0.0, description="Maximum pollution level")
    number: int = Field(default=3, gt=0, description="Number of grids")
    size: int = Field(default=utils.DEFAULT_GRID_SIZE, gt=0, description="Grid size")

    model_config = {"extra": "forbid"}


class Grid(BaseModel):
    """A single grid."""

    ident: str = Field(description="grid identifier")
    cells: list[list] = Field(description="grid cells")
    size: int = Field(description="grid size")

    model_config = {"extra": "forbid"}

    def to_csv(self) -> str:
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


def grids_generate(params: GridParams) -> GridList:
    """Generate random grids.

    Parameters:
        params: Data generation parameters.

    Returns:
        Data model including all grids.
    """

    gen = utils.UniqueIdGenerator("grid", _grid_id_generator)
    grids = []
    for _ in range(params.number):
        grids.append(_make_grid(params, gen.next()))
    return GridList(grids=grids)


def _grid_id_generator() -> str:
    """Generate unique ID for a grid.

    Returns:
        Candidate ID 'gNNN'.
    """

    num = random.randint(0, 999)
    return f"G{num:03d}"


def _make_grid(params: GridParams, ident: str) -> Grid:
    """Create a grid of specified size and fill with random values.

    Parameters:
        params: Data generation parameters.
        ident: Unique ID for this grid

    Returns:
        A single grid.
    """

    cells = [[0.0 for _ in range(params.size)] for _ in range(params.size)]
    center = params.size // 2
    cells[center][center] = _make_value(params.limit)

    radial_groups = _make_radial_groups(params.size)
    for inv_dist in sorted(radial_groups.keys()):
        points = radial_groups[inv_dist]
        temp = []
        for x, y in points:
            temp.append((x, y, _make_value(params.limit * inv_dist)))
        for x, y, val in temp:
            cells[x][y] = val

    return Grid(ident=ident, size=params.size, cells=cells)


def _make_radial_groups(size: int) -> dict:
    """Group points by distance from center.

    Parameters:
        size: Grid size.

    Returns:
        Dictionary of inverse distance to set of points.
    """
    groups = defaultdict(set)
    center = size // 2
    for x in range(size):
        for y in range(size):
            if (x == center) and (y == center):
                continue
            inv_dist = center - math.sqrt((x - center) ** 2 + (y - center) ** 2) / size
            groups[inv_dist].add((x, y))
    return groups


def _make_value(upper: float) -> float:
    """Make a rounded random value in [upper/2, upper].

    Parameters:
        upper: Largest allowed value.

    Returns:
        Rounded random value.
    """

    return round(random.uniform(upper / 2, upper), utils.PRECISION)
