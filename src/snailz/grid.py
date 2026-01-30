"""Sampling grids."""

from dataclasses import dataclass, field
import itertools
from pathlib import Path
import random
from typing import ClassVar, Generator
from .utils import GRID_STD_DEV, BaseMixin, id_generator, lat_lon, validate, validate_lat_lon


# Legal moves for random walk that fills grid.
MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]]

# Grid separation as a multiple of total grid size.
GRID_SEP = 4

# Decimal places in grid values.
GRID_PRECISION = 2


@dataclass
class Grid(BaseMixin):
    """Create and fill a grid."""

    primary_key: ClassVar[str] = "ident"
    pivot_keys: ClassVar[list[str]] = ["cells"]
    table_name: ClassVar[str] = "grid"
    _next_id: ClassVar[Generator[str, None, None]] = id_generator("G", 4)

    ident: str = ""
    size: int = 0
    spacing: float = 0.0
    lat0: float = 0.0
    lon0: float = 0.0
    cells: list = field(default_factory=list)

    def __post_init__(self):
        """Validate and fill in."""

        validate(self.ident == "", "grid ID cannot be set externally")
        validate(self.size > 0, f"grid size must be positive not {self.size}")
        validate(
            self.spacing > 0.0, f"grid spacing must be positive not {self.spacing}"
        )
        validate_lat_lon("grid", self.lat0, self.lon0)

        self.ident = next(self._next_id)
        self.cells = [0 for _ in range(self.size * self.size)]
        self.fill()
        self.randomize()

    @classmethod
    def make(cls, params):
        """Construct multiple grids."""

        origins = cls._make_origins(params)
        return [
            Grid(
                size=params.grid_size,
                spacing=params.grid_spacing,
                lat0=origin[0],
                lon0=origin[1],
            )
            for origin in origins
        ]

    @classmethod
    def save_csv(cls, outdir, objects):
        """Save objects as CSV."""

        super().save_csv(outdir, objects)

        with open(Path(outdir, f"grid_cells.csv"), "w", newline="") as stream:
            objects = cls._ensure_iterable(objects)
            objects = cls._grid_cells(objects)
            exemplar = objects[0]
            writer = cls._csv_dict_writer(stream, list(exemplar.keys()))
            for obj in objects:
                writer.writerow(obj)


    @classmethod
    def save_db(cls, db, objects):
        """Save objects to database."""

        super().save_db(db, objects)

        table = db["grid_cells"]
        table.insert_all(
            cls._grid_cells(objects),
            pk=("grid_id", "lat", "lon"),
            foreign_keys=[("grid_id", "grid", "ident")],
        )

    @classmethod
    def _grid_cells(cls, objects):
        """Get grid cells in long format for persistence."""

        return [
            {"grid_id": g.ident, **g.lat_lon(x, y, True), "value": g[x, y]}
            for g in objects
            for x in range(g.size)
            for y in range(g.size)
        ]

    def __str__(self):
        """Convert grid values to headerless CSV text."""
        return "\n".join(
            ",".join(str(self[x, y]) for x in range(self.size))
            for y in range(self.size - 1, -1, -1)
        )

    def __getitem__(self, key):
        """Get grid element."""

        x, y = key
        return self.cells[x * self.size + y]

    def __setitem__(self, key, value):
        """Set grid element."""

        x, y = key
        self.cells[x * self.size + y] = value

    def fill(self):
        """Fill in a grid."""

        center = self.size // 2
        size_1 = self.size - 1
        x, y = center, center

        while (x != 0) and (y != 0) and (x != size_1) and (y != size_1):
            self[x, y] += 1
            m = random.choice(MOVES)
            x += m[0]
            y += m[1]

    def lat_lon(self, x, y, as_dict=False):
        """Calculate latitude and longitude of grid cell."""

        lat, lon = lat_lon(self.lat0, self.lon0, x * self.spacing, y * self.spacing)
        if as_dict:
            return {"lat": lat, "lon": lon}
        else:
            return lat, lon

    def randomize(self):
        """Randomize values in grid."""

        for i, val in enumerate(self.cells):
            if val > 0.0:
                self.cells[i] = round(abs(random.normalvariate(self.cells[i], GRID_STD_DEV)), GRID_PRECISION)
            else:
                self.cells[i] = 0.0

    @classmethod
    def _make_origins(cls, params):
        """Construct grid origins."""

        possible = list(
            itertools.product(range(params.num_grids), range(params.num_grids))
        )
        actual = random.sample(possible, k=params.num_grids)
        dim = params.grid_size * params.grid_spacing * GRID_SEP
        return [lat_lon(params.lat0, params.lon0, x * dim, y * dim) for x, y in actual]
