"""Sample grids."""

import random
from typing import ClassVar

from pydantic import BaseModel, Field

from . import utils


# Legal moves for random walk that fills grid.
MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]]


class Grid(BaseModel):
    """Create and fill an integer grid."""

    id_stem: ClassVar[str] = "G"
    id_digits: ClassVar[int] = 4

    id: str = Field(min_length=1, description="unique ID")
    size: int = Field(
        gt=0,
        description="grid size",
    )
    grid: list = Field(default=[], description="grid values")

    @staticmethod
    def make(params):
        """Make a grid."""

        utils.ensure_id_generator(Grid)
        grid = Grid(id=next(Grid._id_gen), size=params.grid_size)
        grid.fill()
        return grid

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
