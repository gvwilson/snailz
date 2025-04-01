"""Test grid generation."""

import csv
import io
import math
import pytest
import random

from pydantic import ValidationError

from snailz.defaults import DEFAULT_GRID_PARAMS
from snailz.grid import Grid, GridParams, grid_generate
from snailz.utils import Point, PRECISION

from utils import check_params_stored


@pytest.mark.parametrize(
    "name, value",
    [
        ("depth", 0),
        ("depth", -1),
        ("size", 0),
        ("size", -5),
        ("extra", 1.0),
    ],
)
def test_grid_fail_bad_parameter_value(name, value):
    """Test grid generation fails with invalid parameter values."""
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    params_dict[name] = value
    with pytest.raises(ValidationError):
        GridParams(**params_dict)


def test_grid_fail_missing_parameter():
    """Test grid generation fails with missing parameters."""
    params_dict = DEFAULT_GRID_PARAMS.model_dump()
    del params_dict["depth"]
    with pytest.raises(ValueError):
        GridParams(**params_dict)


@pytest.mark.parametrize("seed", [127893, 47129, 990124, 512741, 44109318])
def test_grid_valid_structure(seed):
    """Test that generated grids have the correct structure."""
    random.seed(seed)
    params = DEFAULT_GRID_PARAMS.model_copy(update={"seed": seed})
    result = grid_generate(params)
    check_params_stored(params, result)

    # Check grid has correct structure
    assert len(result.grid) == params.size
    assert all(len(row) == params.size for row in result.grid)

    # Check grid values are in the correct range 0..depth
    for row in result.grid:
        for cell in row:
            assert 0 <= cell <= params.depth


def test_grid_deterministic_with_same_seed():
    """Test that grids generated with the same seed are identical."""
    seed = 12345
    random.seed(seed)
    grid1 = grid_generate(DEFAULT_GRID_PARAMS)

    random.seed(seed)
    grid2 = grid_generate(DEFAULT_GRID_PARAMS)

    assert grid1.grid == grid2.grid


def test_grid_different_with_different_seeds():
    """Test that grids generated with different seeds are different."""

    random.seed(123)
    grid1 = grid_generate(DEFAULT_GRID_PARAMS)

    random.seed(456)
    grid2 = grid_generate(DEFAULT_GRID_PARAMS)

    assert grid1.grid != grid2.grid


@pytest.mark.parametrize("size", [5, 10, 15])
def test_grid_shape_with_different_sizes(size):
    """Test that grid size parameter properly affects dimensions."""
    params = DEFAULT_GRID_PARAMS.model_copy(update={"size": size})
    result = grid_generate(params)
    assert len(result.grid) == size
    assert all(len(row) == size for row in result.grid)


@pytest.mark.parametrize("depth", [3, 5, 10])
def test_grid_depth_affects_values(depth):
    """Test that depth parameter affects the range of values in the grid."""
    params = DEFAULT_GRID_PARAMS.model_copy(update={"depth": depth})
    result = grid_generate(params)
    filled_cells = [cell for row in result.grid for cell in row]
    assert all(0 <= cell <= depth for cell in filled_cells)


@pytest.mark.parametrize("size", [3, 5, 10])
def test_grid_has_filled_border_cell(size):
    """Test that the filled grid creates a path to the border."""
    params = DEFAULT_GRID_PARAMS.model_copy(update={"size": size})
    result = grid_generate(params)

    # Check borders for filled cells
    size = params.size
    border_cells = []

    # Top and bottom rows
    border_cells.extend(result.grid[0])
    border_cells.extend(result.grid[params.size - 1])

    # Left and right columns (excluding corners already counted)
    for y in range(1, params.size - 1):
        border_cells.append(result.grid[y][0])
        border_cells.append(result.grid[y][size - 1])

    # At least one border cell should be filled (non-zero)
    assert any(cell > 0 for cell in border_cells)


@pytest.mark.parametrize("size", [3, 5, 10])
def test_grid_start_point_filled(size):
    """Test that the start point is always filled."""
    params = DEFAULT_GRID_PARAMS.model_copy(update={"size": size})
    result = grid_generate(params)

    # Check that start point is recorded
    assert result.start.x is not None
    assert result.start.y is not None

    # Check that start point is filled
    assert result.grid[result.start.x][result.start.y] > 0


def test_grid_values_are_rounded():
    """Test that grid values are rounded to PRECISION decimal places."""
    params = DEFAULT_GRID_PARAMS.model_copy()
    result = grid_generate(params)

    for row in result.grid:
        for cell in row:
            if cell > 0:  # Only check filled cells
                # Check that the value has the correct number of decimal places
                # by converting to string and checking characters after decimal point
                cell_str = str(cell)
                if "." in cell_str:
                    decimal_part = cell_str.split(".")[1]
                    assert len(decimal_part) <= PRECISION


def test_grid_real_number_properties():
    """Test properties of the real number grid values."""
    random.seed(12345)
    params = DEFAULT_GRID_PARAMS.model_copy(update={"size": 20})
    result = grid_generate(params)

    # Get all filled cell values
    filled_values = [cell for row in result.grid for cell in row if cell > 0]

    # We should have at least some filled cells
    assert len(filled_values) > 0

    # Calculate distance from start to each filled cell
    start_x, start_y = result.start.x, result.start.y
    cells_with_distance = []

    for x in range(params.size):
        for y in range(params.size):
            value = result.grid[x][y]
            if value > 0:
                distance = math.sqrt((x - start_x) ** 2 + (y - start_y) ** 2)
                cells_with_distance.append((value, distance))

    # Sort by distance
    cells_with_distance.sort(key=lambda x: x[1])

    # Check that values generally decrease with distance
    # We can't check each individual cell due to the influence of original values,
    # but we can check average values for cells at similar distances
    near_cells = [v for v, d in cells_with_distance if d < params.size / 4]
    far_cells = [v for v, d in cells_with_distance if d > params.size / 2]

    if near_cells and far_cells:
        avg_near = sum(near_cells) / len(near_cells)
        avg_far = sum(far_cells) / len(far_cells)

        # Near cells should generally have higher values than far cells
        assert avg_near > avg_far


def test_grid_to_csv():
    """Test grid to_csv method creates CSV representation."""
    grid_data = [[0.0, 3.0, 0.0], [2.0, 0.0, 1.0], [0.0, 4.0, 0.0]]
    grid = Grid(
        grid=grid_data,
        params={"size": 3, "depth": 4, "seed": 12345},
        start=Point(x=1, y=1),
    )

    csv_content = grid.to_csv()
    rows = list(csv.reader(io.StringIO(csv_content)))

    # Check the output
    assert len(rows) == 3
    assert rows[0] == ["0.0", "3.0", "0.0"]
    assert rows[1] == ["2.0", "0.0", "1.0"]
    assert rows[2] == ["0.0", "4.0", "0.0"]
