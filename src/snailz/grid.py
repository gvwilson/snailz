"""Grid generation.

To create a grid using invasion percolation:

1.  Generate an NxN grid of random numbers.
2.  Mark the center cell as "filled" by negating its value.
3.  On each iteration:
    1.  Find the lowest-valued cell adjacent to the filled region.
    2.  Fill that in by negating its value.
    3.  If several cells tie for lowest value, pick one at random.
4.  Stop when the filled region hits the edge of the grid.

Instead of repeatedly searching for cells adjacent to the filled
region, the grid keeps a value-to-coordinates dictionary.  When a cell
is filled in, neighbors not already recorded are added.

The grid is saved as a list of lists. 0 shows unfilled cells, while
positive numbers show the original value of filled cells.
"""

import csv
import io
import random

from pydantic import BaseModel, Field


class GridParams(BaseModel):
    """Parameters for grid generation.

    This class validates the parameters used for grid generation with the following fields:

    - depth: The maximum value for grid cells (must be positive)
    - seed: Random seed for reproducibility
    - size: Grid size (size × size, must be positive)
    """

    depth: int = Field(gt=0, description="The maximum value for grid cells")
    seed: int = Field(description="Random seed for reproducibility")
    size: int = Field(gt=0, description="Grid size (size × size)")

    model_config = {"extra": "forbid"}


class Grid(BaseModel):
    """Keep track of generated grid."""

    grid: list[list[int]]
    params: GridParams

    def to_csv(self) -> str:
        """Return a CSV string representation of the grid data.

        Returns:
            A CSV-formatted string containing the grid values without a header row,
            using Unix line endings (LF).
        """
        output = io.StringIO(newline="\n")
        writer = csv.writer(output, lineterminator="\n")
        for row in self.grid:
            writer.writerow(row)

        return output.getvalue()


def grid_generate(params: GridParams) -> Grid:
    """Generate grid using invasion percolation.

    Parameters:
        params: GridParams object containing depth, seed, size

    Returns:
        Grid object containing the generated grid and parameters
    """
    invperc = Invperc(params.depth, params.size)
    invperc.fill()
    return Grid(grid=invperc.cells, params=params)


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

    def __str__(self) -> str:
        """Convert to printable string representation.

        Returns:
            A string representation of the grid with '.' for unfilled cells
            and 'x' for filled cells, with each row on a separate line
        """
        rows = []
        for y in range(self._size - 1, -1, -1):
            rows.append(
                "".join(
                    "." if self._cells[x][y] == 0 else "x" for x in range(self._size)
                )
            )
        return "\n".join(rows)

    @property
    def cells(self) -> list[list[int]]:
        """Get the grid cell values.

        Returns:
            A 2D list of grid cell values
        """
        return self._cells

    def fill(self) -> None:
        """Fill the grid one cell at a time using invasion percolation.

        Starts at the center and fills outward, choosing lowest-valued adjacent cells,
        until reaching the border of the grid. After filling, inverts cell values.
        """
        x, y = self._size // 2, self._size // 2
        self._cells[x][y] = -self._cells[x][y]
        self.add_candidates(x, y)
        while True:
            x, y = self.choose_cell()
            self._cells[x][y] = -self._cells[x][y]
            if self.on_border(x, y):
                break
        self.invert()

    def invert(self) -> None:
        """Flip cell values to final form.

        Converts negative values (filled cells) to their positive values
        and leaves non-negative values as 0 (unfilled)
        """
        for row in self._cells:
            for i in range(self._size):
                row[i] = 0 if row[i] >= 0 else -row[i]

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
            Chooses the lowest-valued cell adjacent to already filled cells.
            If multiple cells tie for the lowest value, picks one at random.
            Updates the candidate set after selecting a cell.
        """
        min_key = min(self._candidates.keys())
        available = list(sorted(self._candidates[min_key]))
        i = random.randrange(len(available))
        choice = available[i]
        del available[i]
        if not available:
            del self._candidates[min_key]
        else:
            self._candidates[min_key] = set(available)
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
