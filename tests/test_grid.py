"""Tests for grid module."""

import pytest
from snailz.grid import Grid


def test_grid_creation(default_params):
    """Test grid creation with default parameters."""

    grid = Grid.make(default_params)
    assert grid.id.startswith("G")
    assert len(grid.id) == 5  # G + 4 digits
    assert grid.size == default_params.grid_size
    assert len(grid.grid) == grid.size * grid.size


@pytest.mark.parametrize("ident,size", [["", 5], ["G0001", 0], ["G0001", -1]])
def test_grid_parameter_validation(ident, size):
    """Test invalid grid parameters are rejected."""

    with pytest.raises(ValueError):
        Grid(id=ident, size=size)


def test_grid_indexing():
    """Test grid indexing operations."""

    grid = Grid(id="G0001", size=3)
    grid.grid = [i for i in range(9)]  # 0-8

    # Getting values
    assert grid[0, 0] == 0
    assert grid[1, 0] == 1
    assert grid[0, 1] == 3
    assert grid[2, 2] == 8

    # Setting values
    grid[1, 1] = 99
    assert grid[1, 1] == 99


def test_grid_csv_output():
    """Test grid CSV string output."""

    grid = Grid(id="G0001", size=2)
    grid.grid = [1, 2, 3, 4]  # [[1,2], [3,4]]
    csv_output = str(grid)
    lines = csv_output.split("\n")
    assert len(lines) == 2
    assert lines[0] == "3,4"
    assert lines[1] == "1,2"


def test_grid_unique_ids(default_params):
    """Test that grids get unique IDs."""

    grid1 = Grid.make(default_params)
    grid2 = Grid.make(default_params)
    assert grid1.id != grid2.id


def test_grid_fill_bounds_checking(default_params):
    """Test that fill stops at grid boundaries."""

    grid = Grid.make(default_params)
    for x in range(grid.size):
        for y in range(grid.size):
            if (x == 0) or (y == 0):
                assert grid[x, y] == 0
