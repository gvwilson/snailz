"""Generate random grids."""

from datetime import date, timedelta
import io
import random

from pydantic import BaseModel, Field

from . import utils


MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]]


class Point(BaseModel):
    """A 2D point with x and y coordinates."""

    x: int = Field(ge=0, description="x coordinate")
    y: int = Field(ge=0, description="y coordinate")


class GridParams(BaseModel):
    """Parameters for grid generation."""

    number: int = Field(default=3, gt=0, description="Number of grids")
    size: int = Field(default=utils.DEFAULT_GRID_SIZE, gt=0, description="Grid size")
    start_date: date = Field(
        default=date.fromisoformat("2024-03-01"),
        description="Start date for specimen collection",
    )
    max_interval: int = Field(
        gt=0, default=7, description="Maximum interval between samples"
    )

    model_config = {"extra": "forbid"}


class Grid(BaseModel):
    """A single grid."""

    ident: str = Field(description="grid identifier")
    size: int = Field(description="grid size")
    start_date: date = Field(
        default=date.fromisoformat("2024-03-01"),
        description="Start date for specimen collection",
    )
    end_date: date = Field(
        default=date.fromisoformat("2024-04-30"),
        description="End date for specimen collection",
    )
    cells: list[list[int]] = Field(description="grid cells")

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


class AllGrids(BaseModel):
    """A set of generated grids."""

    items: list[Grid] = Field(description="all grids")

    model_config = {"extra": "forbid"}


def grids_generate(params: GridParams) -> AllGrids:
    """Generate random grids.

    Parameters:
        params: Data generation parameters.

    Returns:
        Data model including all grids.
    """

    gen = utils.UniqueIdGenerator("grid", _grid_id_generator)
    current_date = params.start_date
    items = []
    for _ in range(params.number):
        next_date = current_date + timedelta(
            days=random.randint(1, params.max_interval)
        )
        items.append(_make_grid(params, gen, current_date, next_date))
        current_date = next_date + timedelta(days=1)
    return AllGrids(items=items)


def _grid_id_generator() -> str:
    """Generate unique ID for a grid.

    Returns:
        Candidate ID 'gNNN'.
    """

    num = random.randint(0, 999)
    return f"G{num:03d}"


def _make_grid(
    params: GridParams,
    ident_gen: utils.UniqueIdGenerator,
    start_date: date,
    end_date: date,
) -> Grid:
    """Create a grid of specified size and fill with random values.

    Parameters:
        params: Data generation parameters.
        ident_gen: Unique ID generator for this grid

    Returns:
        A single grid.
    """

    cells = _make_cells(params)
    return Grid(
        ident=ident_gen.next(),
        size=params.size,
        cells=cells,
        start_date=start_date,
        end_date=end_date,
    )


def _make_cells(params: GridParams) -> list[list[int]]:
    """Make grid of random values."""
    size = params.size
    size_1 = size - 1
    center = size // 2

    cells = [[0 for _ in range(size)] for _ in range(size)]
    x, y = center, center
    cells[x][y] = 1
    while (x != 0) and (x != size_1) and (y != 0) and (y != size_1):
        cells[x][y] += 1
        m = random.choice(MOVES)
        x += m[0]
        y += m[1]

    return cells
