"""Test utility functions."""

from datetime import date

from pydantic import BaseModel

from snailz.grid import Grid
from snailz.utils import generic_id_generator, json_dump, max_value


def test_generic_id_generator():
    """Test ID generator functionality."""
    gen = generic_id_generator(lambda i: f"TEST{i}")
    assert next(gen) == "TEST1"
    assert next(gen) == "TEST2"
    assert next(gen) == "TEST3"


def test_json_dump_with_base_model():
    """Test JSON serialization of a Pydantic model."""

    class TestModel(BaseModel):
        name: str
        value: int

    model = TestModel(name="test", value=42)
    result = json_dump(model)

    assert "name" in result
    assert "test" in result
    assert "value" in result
    assert "42" in result


def test_json_dump_with_date():
    """Test JSON serialization of a date object."""
    test_date = date(2025, 1, 1)
    result = json_dump({"date": test_date})

    assert "2025-01-01" in result


def test_max_value():
    """Test finding maximum value across grids."""
    grid1 = Grid(size=2)
    grid2 = Grid(size=2)
    for x in range(grid1.size):
        for y in range(grid1.size):
            grid1[x, y] = x + y
            grid2[x, y] = 10 * (x + y)

    assert max_value([grid1, grid2]) == 20
