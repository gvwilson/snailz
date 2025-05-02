"""Test grid functionality."""

from snailz.grid import Grid


def test_grid_creation():
    grid = Grid(size=3)
    assert grid.size == 3
    assert grid[0, 0] == 0
    assert grid[2, 2] == 0

    grid[1, 2] = 5
    assert grid[1, 2] == 5


def test_grid_generation():
    grid = Grid.generate(size=5)
    assert grid.size == 5
    assert grid.id.startswith("G")

    has_nonzero = False
    for x in range(grid.size):
        for y in range(grid.size):
            has_nonzero = has_nonzero or (grid[x, y] > 0)
    assert has_nonzero


def test_grid_to_string():
    grid = Grid(size=2)
    grid[0, 0] = 1
    grid[0, 1] = 2
    grid[1, 0] = 3
    grid[1, 1] = 4
    assert str(grid) == "2,4\n1,3"
