"""Test grid functionality."""

import io
import csv

from snailz.grid import Grid


def test_grid_creation():
    """Test grid creation and access."""
    grid = Grid(size=3)
    assert grid.size == 3
    assert grid[0, 0] == 0
    assert grid[2, 2] == 0

    grid[1, 2] = 5
    assert grid[1, 2] == 5


def test_grid_generation():
    """Test random grid generation."""
    grid = Grid.generate(size=5)
    assert grid.size == 5
    assert grid.id.startswith("G")

    # Check if values were added (at least one cell should be non-zero)
    has_nonzero = False
    for x in range(grid.size):
        for y in range(grid.size):
            if grid[x, y] > 0:
                has_nonzero = True
                break
    assert has_nonzero


def test_grid_to_csv():
    """Test grid to CSV conversion."""
    grid = Grid(size=2)
    grid[0, 0] = 1
    grid[0, 1] = 2
    grid[1, 0] = 3
    grid[1, 1] = 4

    output = io.StringIO()
    writer = csv.writer(output)
    Grid.to_csv(writer, grid)

    result = output.getvalue().strip().split("\n")
    assert "2,4" in result[0]
    assert "1,3" in result[1]


def test_grid_to_string():
    """Test grid string conversion using __str__."""
    grid = Grid(size=2)
    grid[0, 0] = 1
    grid[0, 1] = 2
    grid[1, 0] = 3
    grid[1, 1] = 4

    # Convert grid to string
    grid_str = str(grid)

    # The string should contain all values in CSV format
    assert "1,2" in grid_str
    assert "3,4" in grid_str

    # Parse the resulting CSV string
    lines = [line.strip() for line in grid_str.strip().split("\n") if line.strip()]
    assert len(lines) == 2

    # Each line should have 2 values (for a 2x2 grid)
    for line in lines:
        values = line.split(",")
        assert len(values) == 2
        # Verify all values are digits
        for value in values:
            assert value.isdigit()
