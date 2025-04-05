"""Test grid."""

import pytest

from snailz.grid import Grid


@pytest.mark.parametrize(
    "i", [(-1, 0), (0, -1), (5, 0), (0, 5), "oops", (), (0.1, 0), (0, 0.1)]
)
def test_grid_indices(i):
    grid = Grid[int](width=3, height=3, default=0)
    with pytest.raises((IndexError, KeyError)):
        grid[*i]
    with pytest.raises((IndexError, KeyError)):
        grid[*i] = 1


def test_grid_string_representation():
    grid = Grid[str](width=3, height=3, default="a")
    assert str(grid) == "a,a,a\na,a,a\na,a,a"
