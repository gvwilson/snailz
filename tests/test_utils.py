"""Test utility functions."""

import json
import pytest
from datetime import date
from pydantic import BaseModel

from click.testing import CliRunner

from snailz.clui import convert
from snailz.defaults import DEFAULT_GRID_PARAMS
from snailz.grid import Grid
from snailz.utils import load_data, report_result, serialize_values, validate_date


class ValueClass(BaseModel):
    """Pydantic model for utility tests."""

    name: str
    value: int = 0
    date_value: date = None
    items: list = []


def test_load_data_valid_json(fs):
    """Test that load_data correctly loads valid JSON into a dataclass."""
    # Test data
    test_data = {"name": "test", "value": 42}
    test_file = "/test.json"
    fs.create_file(test_file, contents=json.dumps(test_data))

    result = load_data("test", test_file, ValueClass)

    assert isinstance(result, ValueClass)
    assert result.name == "test"
    assert result.value == 42


def test_load_data_missing_file(fs):
    """Test that load_data raises an error for missing files."""
    test_file = "/nonexistent.json"
    with pytest.raises(FileNotFoundError):
        load_data("test", test_file, ValueClass)


def test_load_data_invalid_json(fs):
    """Test that load_data raises an error for invalid JSON."""
    test_file = "/invalid.json"
    fs.create_file(test_file, contents="{invalid json")
    with pytest.raises(json.JSONDecodeError):
        load_data("test", test_file, ValueClass)


def test_load_data_incompatible_data(fs):
    """Test that load_data raises an error when JSON doesn't match dataclass."""
    # Use a completely incompatible data structure
    test_data = {"wrong_field": "test", "another_wrong": 42}
    test_file = "/incompatible.json"
    fs.create_file(test_file, contents=json.dumps(test_data))
    with pytest.raises(Exception):
        load_data("test", test_file, ValueClass)


def test_load_data_empty_filename():
    """Test that load_data raises an assertion error for empty filenames."""
    with pytest.raises(IOError):
        load_data("test", "", ValueClass)


def test_report_result_to_file(fs):
    """Test that report_result writes to a file when output is specified."""
    test_data = ValueClass(
        name="Test Result", date_value=date(2025, 3, 22), items=[1, 2, 3]
    )
    output_file = "/output.json"

    report_result(output_file, test_data)

    assert fs.exists(output_file)
    with open(output_file, "r") as f:
        content = json.load(f)
        assert content["name"] == "Test Result"
        assert content["date_value"] == "2025-03-22"  # ISO format
        assert content["items"] == [1, 2, 3]


def test_report_result_to_stdout(capsys):
    """Test that report_result writes to stdout when output is not specified."""
    test_data = ValueClass(
        name="Test Result", date_value=date(2025, 3, 22), items=[1, 2, 3]
    )

    report_result(None, test_data)

    captured = capsys.readouterr()
    content = json.loads(captured.out)
    assert content["name"] == "Test Result"
    assert content["date_value"] == "2025-03-22"  # ISO format
    assert content["items"] == [1, 2, 3]


def test_serialize_values():
    """Test that serialize_values correctly handles dates and floats."""
    test_date = date(2025, 3, 22)
    result = serialize_values(test_date)
    assert result == "2025-03-22"

    with pytest.raises(TypeError):
        serialize_values("not a date or float")


def test_validate_date():
    """Test that validate_date converts string to date object."""
    # Test with valid date string
    result = validate_date(None, None, "2025-03-22")
    assert isinstance(result, date)
    assert result.year == 2025
    assert result.month == 3
    assert result.day == 22

    # Test with None returns None
    assert validate_date(None, None, None) is None


def test_convert_command_integration(fs):
    """Test CSV conversion."""
    grid_data = Grid(
        grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        params=DEFAULT_GRID_PARAMS,
    )

    grid_file = "/test_grid.json"
    fs.create_file(
        grid_file,
        contents=json.dumps(
            {"grid": grid_data.grid, "params": grid_data.params},
            default=serialize_values,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(convert, ["--input", grid_file, "--kind", "grid"])
    assert result.exit_code == 0

    assert "0,1,2" in result.output
    assert "3,4,5" in result.output
    assert "6,7,8" in result.output
