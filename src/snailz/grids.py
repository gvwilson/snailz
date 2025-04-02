"""Generate random grids."""

import io
import random

from pydantic import BaseModel, Field

from . import utils


class GridParams(BaseModel):
    """Parameters for grid generation."""

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
        grids.append(_make_grid(gen.next(), parameters.size))
    return GridList(grids=grids)


def _grid_id_generator():
    """Generate unique ID for a grid (CNNN)."""

    num = random.randint(0, 999)
    return f"G{num:03d}"


def _make_grid(ident, size):
    """Create a grid of specified size."""

    cells = [[0 for _ in range(size)] for _ in range(size)]
    return Grid(ident=ident, size=size, cells=cells)
