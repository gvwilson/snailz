"""Test grid generation."""

import csv
import io
import pytest
import random

from snailz.defaults import DEFAULT_GRID_PARAMS
from snailz.grid import grid_generate, Invperc, Grid, GridParams

from utils import check_params_stored


@pytest.mark.parametrize(
    "name, value",
    [
        ("depth", 0),
        ("depth", -1),
        ("size", 0),
        ("size", -5),
    ],
)
def test_grid_fail_bad_parameter_value(name, value):
    """Test grid generation fails with invalid parameter values."""
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    params_dict[name] = value
    with pytest.raises(ValueError):
        GridParams(**params_dict)


def test_grid_fail_missing_parameter():
    """Test grid generation fails with missing parameters."""
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    del params_dict["depth"]
    with pytest.raises(ValueError):
        GridParams(**params_dict)


def test_grid_fail_extra_parameter():
    """Test grid generation fails with extra parameters."""
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    params_dict["extra"] = 1.0
    with pytest.raises(ValueError):
        GridParams(**params_dict)


@pytest.mark.parametrize("seed", [127893, 47129, 990124, 512741, 44109318])
def test_grid_valid_structure(seed):
    """Test that generated grids have the correct structure."""
    random.seed(seed)
    # Create a new params object with updated seed
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    params_dict["seed"] = seed
    params = GridParams(**params_dict)
    result = grid_generate(params)
    check_params_stored(params, result)

    # Check grid has correct structure
    assert len(result.grid) == params.size
    assert all(len(row) == params.size for row in result.grid)

    # Check grid values are in the correct range (0 or 1..depth)
    for row in result.grid:
        for cell in row:
            assert cell == 0 or 1 <= cell <= params.depth


def test_grid_deterministic_with_same_seed():
    """Test that grids generated with the same seed are identical."""
    seed = 12345
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    params_dict["seed"] = seed
    params = GridParams(**params_dict)

    # Generate two grids with the same seed
    random.seed(seed)  # Set seed before each grid generation
    grid1 = grid_generate(params)

    random.seed(seed)  # Reset seed for the second grid
    grid2 = grid_generate(params)

    # They should be identical
    assert grid1.grid == grid2.grid


def test_grid_different_with_different_seeds():
    """Test that grids generated with different seeds are different."""
    # First grid with seed 123
    params_dict1 = DEFAULT_GRID_PARAMS.model_dump()
    params_dict1["seed"] = 123
    random.seed(123)
    grid1 = grid_generate(GridParams(**params_dict1))

    # Second grid with seed 456
    params_dict2 = DEFAULT_GRID_PARAMS.model_dump()
    params_dict2["seed"] = 456
    random.seed(456)
    grid2 = grid_generate(GridParams(**params_dict2))

    # They should be different
    assert grid1.grid != grid2.grid


def test_grid_shape_with_different_sizes():
    """Test that grid size parameter properly affects dimensions."""
    sizes = [5, 10, 15]
    for size in sizes:
        params_dict = DEFAULT_GRID_PARAMS.model_dump()
        params_dict["size"] = size
        params = GridParams(**params_dict)
        result = grid_generate(params)

        # Check dimensions
        assert len(result.grid) == size
        assert all(len(row) == size for row in result.grid)


def test_grid_depth_affects_values():
    """Test that depth parameter affects the range of values in the grid."""
    depth_values = [3, 5, 10]
    for depth in depth_values:
        params_dict = DEFAULT_GRID_PARAMS.model_dump()
        params_dict["depth"] = depth
        params = GridParams(**params_dict)
        result = grid_generate(params)

        # Check that non-zero values are within range 1..depth
        filled_cells = [cell for row in result.grid for cell in row if cell > 0]
        assert all(1 <= cell <= depth for cell in filled_cells)


def test_grid_has_path_to_border():
    """Test that the filled grid creates a path to the border."""
    # Use a smaller grid for this test
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    params_dict["size"] = 10
    params = GridParams(**params_dict)
    result = grid_generate(params)

    # The algorithm should fill cells from center to border
    # So we should have at least one filled cell on the border

    # Check borders for filled cells
    size = params.size
    border_cells = []

    # Top and bottom rows
    border_cells.extend(result.grid[0])
    border_cells.extend(result.grid[size - 1])

    # Left and right columns (excluding corners already counted)
    for y in range(1, size - 1):
        border_cells.append(result.grid[y][0])
        border_cells.append(result.grid[y][size - 1])

    # At least one border cell should be filled (non-zero)
    assert any(cell > 0 for cell in border_cells)


def test_grid_center_always_filled():
    """Test that the center cell is always filled."""
    # Try different size grids
    for size in [5, 7, 9]:
        params_dict = DEFAULT_GRID_PARAMS.model_dump()
        params_dict["size"] = size
        params = GridParams(**params_dict)
        result = grid_generate(params)

        # Center should be filled (non-zero)
        center_x = center_y = size // 2
        assert result.grid[center_x][center_y] > 0


def test_invperc_string_representation():
    """Test the string representation of the Invperc class."""
    # Create a simple 3x3 grid with known values
    invperc = Invperc(5, 3)

    # Build a simple test grid where we control which cells are filled
    # Initialize with all zeros (unfilled)
    invperc._cells = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    # Set a few specific cells as filled (non-zero)
    # Important: looking at the __str__ implementation, rows are rendered in reverse order
    # and '.' is unfilled (0), 'x' is filled (non-zero)
    invperc._cells[0][0] = 0  # bottom left: unfilled
    invperc._cells[1][0] = 2  # bottom middle: filled
    invperc._cells[2][0] = 0  # bottom right: unfilled
    invperc._cells[0][1] = 0  # middle left: unfilled
    invperc._cells[1][1] = 3  # center: filled
    invperc._cells[2][1] = 0  # middle right: unfilled
    invperc._cells[0][2] = 0  # top left: unfilled
    invperc._cells[1][2] = 0  # top middle: unfilled
    invperc._cells[2][2] = 1  # top right: filled

    # Generate string representation
    str_rep = str(invperc)

    # The grid should look like:
    # [0,0,0][0,0,1]
    # [0,3,0][0,x,0]
    # [0,2,0][.x.]

    # Given how the __str__ method works (y goes down to up, print top to bottom)
    # Expected output should be:
    expected = "..x\n.x.\n.x."

    assert str_rep == expected


def test_invperc_on_border():
    """Test the on_border method of Invperc class."""
    invperc = Invperc(5, 5)

    # Test border cells
    assert invperc.on_border(0, 0)  # Top-left corner
    assert invperc.on_border(0, 2)  # Left edge
    assert invperc.on_border(2, 0)  # Top edge
    assert invperc.on_border(4, 4)  # Bottom-right corner
    assert invperc.on_border(4, 2)  # Right edge
    assert invperc.on_border(2, 4)  # Bottom edge

    # Test non-border cells
    assert not invperc.on_border(1, 1)
    assert not invperc.on_border(2, 2)  # Center
    assert not invperc.on_border(3, 2)


@pytest.fixture
def sample_grid():
    """Create a small test grid."""
    grid_data = [[0, 3, 0], [2, 0, 1], [0, 4, 0]]
    return Grid(grid=grid_data, params={"size": 3, "depth": 4, "seed": 12345})


def test_grid_to_csv(sample_grid):
    """Test grid to_csv method creates CSV representation."""
    # Get the CSV content
    csv_content = sample_grid.to_csv()

    # Parse the CSV output
    rows = list(csv.reader(io.StringIO(csv_content)))

    # Check the output
    assert len(rows) == 3
    assert rows[0] == ["0", "3", "0"]
    assert rows[1] == ["2", "0", "1"]
    assert rows[2] == ["0", "4", "0"]

    # Check that we have Unix line endings (LF) but no DOS line endings (CRLF)
    assert "\n" in csv_content
    assert "\r\n" not in csv_content
