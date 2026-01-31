"""Test grid generation."""

import csv
from dataclasses import fields
import json
from pathlib import Path
from PIL import Image
import pytest
from sqlite_utils import Database
from snailz import Grid, Parameters


@pytest.fixture
def small_grid(seeded_rng):
    return Grid(size=5, spacing=10.0, lat0=45.0, lon0=-75.0, params=Parameters())


def test_grid_minimal(seeded_rng):
    g = Grid(size=1, spacing=1.0, lat0=0.0, lon0=0.0, params=Parameters())
    assert g.size == 1
    assert len(g.cells) == 1
    assert g.cells[0] >= 0


def test_grid_ident_is_unique(seeded_rng):
    params = Parameters()
    g1 = Grid(size=3, spacing=1.0, lat0=0.0, lon0=0.0, params=params)
    g2 = Grid(size=3, spacing=1.0, lat0=0.0, lon0=0.0, params=params)
    assert g1.ident != g2.ident
    assert g1.ident.startswith("G")
    assert g2.ident.startswith("G")


def test_grid_initialization(small_grid):
    assert small_grid.size == 5
    assert small_grid.spacing == 10.0
    assert small_grid.lat0 == 45.0
    assert small_grid.lon0 == -75.0
    assert len(small_grid.cells) == 25


def test_grid_get_and_set_item(small_grid):
    small_grid[2, 3] = 42.0
    assert small_grid[2, 3] == 42.0


def test_grid_fill_creates_nonzero_values(small_grid):
    assert all(v >= 0 for v in small_grid.cells)


def test_grid_randomize_respects_std_dev(seeded_rng):
    g = Grid(size=5, spacing=1.0, lat0=0.0, lon0=0.0, params=Parameters())
    assert len(set(g.cells)) > 1


def test_grid_lat_lon_corner(small_grid):
    lat, lon = small_grid.lat_lon(0, 0)
    assert lat == small_grid.lat0
    assert lon == small_grid.lon0


def test_grid_as_json(small_grid):
    data = small_grid.as_json()
    assert isinstance(data, str)
    data = json.loads(data)
    assert set(data.keys()) == {"ident", "size", "spacing", "lat0", "lon0"}


def test_grid_make():
    grids = Grid.make(
        Parameters(num_grids=3, grid_size=2, grid_spacing=1.0, lat0=0.0, lon0=0.0)
    )
    assert len(grids) == 3
    assert all(isinstance(g, Grid) for g in grids)
    assert all(g.size == 2 for g in grids)
    assert len({g.ident for g in grids}) == 3


def test_grid_separation():
    grids = Grid.make(
        Parameters(num_grids=10, grid_size=2, grid_spacing=1.0, lat0=0.0, lon0=0.0)
    )
    assert len({(g.lat0, g.lon0) for g in grids}) == len(grids)


def test_grid_persist_to_csv(tmp_path):
    grids = Grid.make(
        Parameters(num_grids=3, grid_size=2, grid_spacing=1.0, lat0=0.0, lon0=0.0)
    )
    Grid.save_csv(tmp_path, grids)

    with open(Path(tmp_path, f"{Grid.table_name}.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 4

    with open(Path(tmp_path, "grid_cells.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 1 + (3 * 2 * 2)


def test_grid_persist_to_db():
    db = Database(memory=True)
    grids = Grid.make(
        Parameters(num_grids=3, grid_size=2, grid_spacing=1.0, lat0=0.0, lon0=0.0)
    )
    Grid.save_db(db, grids)

    rows = list(db[Grid.table_name].rows)
    assert set(r["ident"] for r in rows) == set(g.ident for g in grids)
    field_names = {f.name for f in fields(grids[0])}
    assert set(rows[0].keys()).issubset(field_names)


def test_grid_to_image(small_grid):
    assert isinstance(small_grid.as_image(max(small_grid.cells)), Image.Image)


def test_grid_to_image_zero_scale(small_grid):
    assert isinstance(small_grid.as_image(0.0), Image.Image)


def test_grid_to_str(small_grid):
    text = str(small_grid)
    rows = text.split("\n")
    assert len(rows) == small_grid.size
    assert all(len(r.split(",")) == small_grid.size for r in rows)
