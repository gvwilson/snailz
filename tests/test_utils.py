"""Test utility functions."""

from datetime import date

from PIL import Image
from pydantic import BaseModel
import pytest

from snailz.grid import Grid
from snailz.utils import generic_id_generator, json_dump, max_grid_value


def test_generic_id_generator():
    gen = generic_id_generator(lambda i: f"TEST{i}")
    assert next(gen) == "TEST1"
    assert next(gen) == "TEST2"
    assert next(gen) == "TEST3"


def test_json_dump_base_model():
    class TestModel(BaseModel):
        name: str
        value: int

    model = TestModel(name="test", value=42)
    result = json_dump(model)

    assert "name" in result
    assert "test" in result
    assert "value" in result
    assert "42" in result


def test_json_dump_date():
    test_date = date(2025, 1, 1)
    result = json_dump({"date": test_date})

    assert "2025-01-01" in result


def test_json_dump_image():
    img = Image.new("1", (100, 100), 0)
    assert '"image": null' in json_dump({"image": img})


def test_json_dump_unknown():
    class Unknown:
        pass

    with pytest.raises(TypeError):
        json_dump({"unknown": Unknown()})


def test_max_grid_value():
    grid1 = Grid(size=2)
    grid2 = Grid(size=2)
    for x in range(grid1.size):
        for y in range(grid1.size):
            grid1[x, y] = x + y
            grid2[x, y] = 10 * (x + y)

    assert max_grid_value([grid1, grid2]) == 20
