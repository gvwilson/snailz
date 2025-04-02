"""Generate random grids."""

import random

from .models import Grid, GridList
from .utils import UniqueIdGenerator


def grids_generate(parameters):
    """Generate random grids."""

    gen = UniqueIdGenerator("grid", _grid_id_generator)
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
