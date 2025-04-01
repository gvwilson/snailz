"""Grid generation.

To create a grid using invasion percolation:

1.  Generate an NxN grid of random numbers.
2.  Mark a cell near the center as filled by negating its value.
3.  On each iteration:
    1.  Find the highest-valued cell adjacent to the filled region.
    2.  Fill that in by negating its value.
    3.  If several cells tie for highest value, pick one at random.
4.  Stop when the filled region hits the edge of the grid.
5.  Convert filled cells to positive real numbers rounded to PRECISION
    decimal places.  The final value depends on the distance from the
    starting cell (decreasing with distance) and on the integer value
    the cell had as it was being filled (higher original values result
    in higher final values).

Instead of repeatedly searching for cells adjacent to the filled
region, the grid keeps a value-to-coordinates dictionary.  When a cell
is filled in, neighbors not already recorded are added.

The grid is saved as a list of lists. 0 shows unfilled cells, while
positive numbers show the final values of filled cells.
"""

import io
import math
import random

from pydantic import BaseModel, Field

from . import utils
from .utils import Point, PRECISION


# Parameters used to calculate final cell values
FRAC_DISTANCE = 0.7
FRAC_VALUE = 0.3


class GridParams(BaseModel):
    """Parameters for grid generation."""

    depth: int = Field(gt=0, description="Maximum value for grid cells")
    seed: int = Field(ge=0, description="Random seed")
    size: int = Field(gt=0, description="Grid size")

    model_config = {"extra": "forbid"}


class Grid(BaseModel):
    """Keep track of generated grid."""

    grid: list[list[float]] = Field(description="Grid cells")
    params: GridParams = Field(description="Parameters used in grid generation")
    start: Point = Field(description="Starting point for invasion percolation")

    def to_csv(self) -> str:
        """Return a CSV string representation of the grid data.

        Returns:
            A CSV-formatted string containing the grid values without a header row.
        """
        output = io.StringIO(newline="\n")
        writer = utils.csv_writer(output)
        for row in self.grid:
            writer.writerow(row)
        return output.getvalue()


def grid_generate(params: GridParams) -> Grid:
    """Generate grid using invasion percolation.

    Parameters:
        params: GridParams object containing depth, seed, size

    Returns:
        Grid object containing the generated grid, parameters, and starting point
    """
    center = params.size // 2
    quarter = params.size // 4
    start_x = random.randint(center - quarter, center + quarter)
    start_y = random.randint(center - quarter, center + quarter)
    start = Point(x=start_x, y=start_y)
    invperc = Invperc(params.depth, params.size)
    invperc.fill(start_x, start_y)
    return Grid(grid=invperc.cells, params=params, start=start)


class Invperc:
    """Represent a 2D grid that supports lazy filling."""

    def __init__(self, depth: int, size: int) -> None:
        """Initialize the invasion percolation grid.

        Parameters:
            depth: The maximum value for grid cells
            size: The size of the grid (size x size)
        """
        self._depth = depth
        self._size = size
        self._cells = []
        for x in range(self._size):
            col = [random.randint(1, self._depth) for y in range(self._size)]
            self._cells.append(col)
        self._candidates = {}

    @property
    def cells(self) -> list[list[float]]:
        """Get the grid cell values.

        Returns:
            A 2D list of grid cell values
        """
        return self._cells

    def fill(self, start_x: int, start_y: int) -> None:
        """Fill the grid one cell at a time using invasion percolation.

        Starts at the specified coordinates and fills outward,
        choosing highest-valued adjacent cells, until reaching the
        border of the grid. After filling, converts cells to real values
        based on distance from start and original cell values.

        Parameters:
            start_x: X-coordinate where filling starts
            start_y: Y-coordinate where filling starts
        """
        # Record fill order and original values
        self._start_x = start_x
        self._start_y = start_y

        # Mark start cell as filled
        self._cells[start_x][start_y] = -self._cells[start_x][start_y]

        self.add_candidates(start_x, start_y)
        while True:
            x, y = self.choose_cell()
            self._cells[x][y] = -self._cells[x][y]
            if self.on_border(x, y):
                break

        self.calculate_final_values()

    def calculate_final_values(self) -> None:
        """Convert cells to real values based on distance from start and original values.

        For filled cells (negative values):
        1. Calculate the Euclidean distance from the starting cell
        2. Create a value that decreases with distance and increases with original cell value
        3. Round to PRECISION decimal places
        4. Unfilled cells (non-negative values) become 0
        """
        max_distance = math.sqrt(2) * self._size / 2
        max_value = self._depth

        for x, row in enumerate(self._cells):
            for y, val in enumerate(row):
                # unfilled cell
                if val >= 0:
                    row[y] = 0.0
                    continue
                distance = math.sqrt(
                    (x - self._start_x) ** 2 + (y - self._start_y) ** 2
                )
                distance_factor = 1.0 - (distance / max_distance)
                value_factor = -val / max_value
                final_value = (
                    FRAC_DISTANCE * distance_factor + FRAC_VALUE * value_factor
                ) * max_value
                row[y] = round(final_value, PRECISION)

    def add_candidates(self, x: int, y: int) -> None:
        """Add unfilled cells adjacent to a filled cell as candidates for filling.

        Parameters:
            x: X-coordinate of the filled cell
            y: Y-coordinate of the filled cell
        """
        for ix in (x - 1, x + 1):
            self.add_one_candidate(ix, y)
        for iy in (y - 1, y + 1):
            self.add_one_candidate(x, iy)

    def add_one_candidate(self, x: int, y: int) -> None:
        """Add a single point to the set of candidates for filling.

        Parameters:
            x: X-coordinate of the candidate cell
            y: Y-coordinate of the candidate cell

        Note:
            Does nothing if the coordinates are outside the grid bounds
            or if the cell is already filled (negative value)
        """
        if (x < 0) or (x >= self._size) or (y < 0) or (y >= self._size):
            return
        if self._cells[x][y] < 0:
            return

        value = self._cells[x][y]
        if value not in self._candidates:
            self._candidates[value] = set()
        self._candidates[value].add((x, y))

    def choose_cell(self) -> tuple[int, int]:
        """Choose the next cell to fill using the invasion percolation algorithm.

        Returns:
            A tuple (x, y) of coordinates for the next cell to fill

        Note:
            Chooses the highest-valued cell adjacent to already filled cells.
            If multiple cells tie for the highest value, picks one at random.
            Updates the candidate set after selecting a cell.
        """
        max_key = max(self._candidates.keys())
        available = list(sorted(self._candidates[max_key]))
        i = random.randrange(len(available))
        choice = available[i]
        del available[i]
        if not available:
            del self._candidates[max_key]
        else:
            self._candidates[max_key] = set(available)
        self.add_candidates(*choice)
        return choice

    def on_border(self, x: int, y: int) -> bool:
        """Check if a cell is on the border of the grid.

        Parameters:
            x: X-coordinate of the cell
            y: Y-coordinate of the cell

        Returns:
            True if the cell is on any edge of the grid, False otherwise
        """
        size_1 = self._size - 1
        return (x == 0) or (x == size_1) or (y == 0) or (y == size_1)
