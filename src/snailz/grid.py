"""Sampling grids."""

from dataclasses import InitVar, dataclass, field
import itertools
import math
import numpy as np
from pathlib import Path
from PIL import Image
import random
from sqlite_utils import Database
from typing import Any, ClassVar, Self

from ._base_mixin import BaseMixin
from ._utils import (
    IdGeneratorType,
    id_generator,
    lat_lon,
    validate,
    validate_lat_lon,
)
from .parameters import Parameters


# Legal moves for random walk that fills grid.
MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]]

# Decimal places in grid values.
GRID_PRECISION = 2

# Image parameters.
BLACK = 0
WHITE = 255
BORDER_WIDTH = 8
CELL_SIZE = 32


@dataclass
class Grid(BaseMixin):
    """
    A single survey grid.

    Attributes:
        ident: unique identifier
        size: grid size in cells
        spacing: size of individual cell (m)
        lat0: reference latitude of cell (0, 0)
        lon0: reference longitude of cell (0, 0)
        cells: pollution measurements for cells
    """

    primary_key: ClassVar[str] = "ident"
    pivot_keys: ClassVar[set[str]] = {"cells"}
    table_name: ClassVar[str] = "grid"
    _next_id: IdGeneratorType = id_generator("G", 4)

    ident: str = ""
    size: int = 0
    spacing: float = 0.0
    lat0: float = 0.0
    lon0: float = 0.0
    cells: list[float] = field(default_factory=list)
    params: InitVar[Parameters] = None

    def __post_init__(self, params: Parameters):
        """
        Validate fields, generate unique identifier, and fill in cells.

        Args:
            params: Parameters object.

        Raises:
            ValueError: If validation fails.
        """

        validate(self.ident == "", "grid ID cannot be set externally")
        validate(self.size > 0, f"grid size must be positive not {self.size}")
        validate(
            self.spacing > 0.0, f"grid spacing must be positive not {self.spacing}"
        )
        validate_lat_lon("grid", self.lat0, self.lon0)
        validate(params is not None, "params required for initializing grid")

        self.ident = next(self._next_id)
        self.cells = [0.0 for _ in range(self.size * self.size)]
        self._fill()
        self._randomize(params)

    def __str__(self) -> str:
        """
        Convert grid values to headerless CSV text.

        Returns:
            Printable CSV string representation of grid values.
        """

        return "\n".join(
            ",".join(str(self[x, y]) for x in range(self.size))
            for y in range(self.size - 1, -1, -1)
        )

    def __getitem__(self, key: tuple[int, int]) -> Any:
        """
        Get grid element.

        Args:
            key: (x, y) coordinates.

        Returns:
            Value at that location.

        Raises:
            ValueError: If either coordinate out of range.
        """

        self._validate_coords(key)
        x, y = key
        return self.cells[x * self.size + y]

    def __setitem__(self, key: tuple[int, int], value: float):
        """
        Set grid element.

        Args:
            key: (x, y) coordinates.
            value: new value.

        Raises:
            ValueError: If either coordinate out of range.
        """

        x, y = key
        self.cells[x * self.size + y] = value

    @classmethod
    def make(cls, params: Parameters) -> list[Self]:
        """
        Construct multiple grids.

        Args:
            params: Parameters object.

        Returns:
            List of grids.
        """

        origins = cls._make_origins(params)
        return [
            Grid(
                size=params.grid_size,
                spacing=params.grid_spacing,
                lat0=origin[0],
                lon0=origin[1],
                params=params,
            )
            for origin in origins
        ]

    @classmethod
    def save_csv(cls, outdir: Path | str, grids: list[Self]):
        """
        Save grids as CSV. Scalar properties of all grids are saved in
        one file; grid cell values are pivoted to long form and saved
        in a separate file.

        Args:
            outdir: Output directory.
            grids: `Grid` objects to save.
        """

        super().save_csv(outdir, grids)

        with open(Path(outdir, "grid_cells.csv"), "w", newline="") as stream:
            objects = cls._grid_cells(grids)
            writer = cls._csv_dict_writer(stream, list(objects[0].keys()))
            for obj in objects:
                writer.writerow(obj)

    @classmethod
    def save_db(cls, db: Database, grids: list[Self]):
        """
        Save grids to database. Scalar properties of all grids are
        saved in one table; grid cell values are pivoted to long form
        and saved in a separate table.

        Args:
            db: Database connector.
            grids: `Grid` objects to save.
        """

        super().save_db(db, grids)

        table = db["grid_cells"]
        table.insert_all(
            cls._grid_cells(grids),
            pk=("grid_id", "lat", "lon"),
            foreign_keys=[("grid_id", "grid", "ident")],
        )

    @classmethod
    def _grid_cells(cls, grids):
        """
        Pivot grid cell values to long format for persistence.

        Args:
            grids: `Grid` objects to pivot.
        """

        return [
            {"grid_id": g.ident, **g.lat_lon(x, y, True), "value": g[x, y]}
            for g in grids
            for x in range(g.size)
            for y in range(g.size)
        ]

    @classmethod
    def _make_origins(cls, params):
        """
        Construct grid origins.

        Args:
            params: Parameters object.

        Returns:
            List of `params.num_grids` (lat, lon) origins.
        """

        possible = list(
            itertools.product(range(params.num_grids), range(params.num_grids))
        )
        actual = random.sample(possible, k=params.num_grids)
        dim = params.grid_size * params.grid_spacing * params.grid_separation
        return [lat_lon(params.lat0, params.lon0, x * dim, y * dim) for x, y in actual]

    def as_image(self, scale: float) -> Image.Image:
        """
        Convert grid to image.

        Args:
            scale: Scaling factor for grid values to ensure largest is black.

        Returns:
            `Image` object.
        """

        scale = scale or self.min_max()[1] or 1.0
        img_size = (self.size * CELL_SIZE) + ((self.size + 1) * BORDER_WIDTH)
        array = np.full((img_size, img_size), WHITE, dtype=np.uint8)
        spacing = CELL_SIZE + BORDER_WIDTH
        for ix, x in enumerate(range(BORDER_WIDTH, img_size, spacing)):
            for iy, y in enumerate(range(BORDER_WIDTH, img_size, spacing)):
                color = WHITE - math.floor(WHITE * self[ix, iy] / scale)
                array[y : y + CELL_SIZE + 1, x : x + CELL_SIZE + 1] = color

        return Image.fromarray(array)

    def lat_lon(
        self, x: int, y: int, as_dict: bool = False
    ) -> tuple[float, float] | dict[str, float]:
        """
        Calculate latitude and longitude of grid cell.

        Args:
            x: Grid X coordinate.
            y: Grid Y coordinate.
            as_dict: Return result as dict instead of pair.

        Returns:
            `(lat, lon)` pair or `{"lat": lat, "lon": lon}` dictionary.

        Raises:
            ValueError: if either coordinate out of range.
        """

        self._validate_coords((x, y))
        lat, lon = lat_lon(self.lat0, self.lon0, x * self.spacing, y * self.spacing)
        return {"lat": lat, "lon": lon} if as_dict else (lat, lon)

    def min_max(self) -> tuple[float, float]:
        """
        Find smallest and largest values in grid.

        Returns:
            `(min, max)` pair.
        """

        return min(self.cells), max(self.cells)

    def _fill(self):
        """Fill in grid values using random walk."""

        center = self.size // 2
        size_1 = self.size - 1
        x, y = center, center

        while (x != 0) and (y != 0) and (x != size_1) and (y != size_1):
            self[x, y] += 1
            m = random.choice(MOVES)
            x += m[0]
            y += m[1]

    def _randomize(self, params: Parameters):
        """
        Randomize values in grid after filling.

        Args:
            params: Parameters object.
        """

        for i, val in enumerate(self.cells):
            if val > 0.0:
                self.cells[i] = round(
                    abs(random.normalvariate(self.cells[i], params.grid_std_dev)),
                    GRID_PRECISION,
                )
            else:
                self.cells[i] = 0.0

    def _validate_coords(self, key: tuple[int, int]):
        """
        Validate (x, y) coordinate pair.

        Raises:
            ValueError: If either coordinate is out of range.
        """
        validate(0 <= key[0] < self.size, "invalid X coordinate {key[0]}")
        validate(0 <= key[1] < self.size, "invalid Y coordinate {key[1]}")
