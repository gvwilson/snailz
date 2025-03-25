"""Test utility functions."""

import json
import pytest
from datetime import date
from pydantic import BaseModel

from click.testing import CliRunner

from snailz.clui import convert
from snailz.grid import Grid, GridParams
from snailz.utils import load_data, report_result, serialize_values, validate_date


class ValueClass(BaseModel):
    """Test Pydantic model for load_data tests."""

    name: str
    value: int


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
    test_data = {"name": "test"}
    test_file = "/incompatible.json"
    fs.create_file(test_file, contents=json.dumps(test_data))
    with pytest.raises(Exception):
        load_data("test", test_file, ValueClass)


def test_load_data_empty_filename():
    """Test that load_data raises an assertion error for empty filenames."""
    with pytest.raises(ValueError):
        load_data("test", "", ValueClass)


class ResultClass(BaseModel):
    """Test Pydantic model for report_result tests."""

    name: str
    date_value: date
    items: list


def test_report_result_to_file(fs):
    """Test that report_result writes to a file when output is specified."""
    # Test data
    test_data = ResultClass(
        name="Test Result", date_value=date(2025, 3, 22), items=[1, 2, 3]
    )
    output_file = "/output.json"

    # Call report_result
    report_result(output_file, test_data)

    # Check that the file was created with correct content
    assert fs.exists(output_file)
    with open(output_file, "r") as f:
        content = json.load(f)
        assert content["name"] == "Test Result"
        assert content["date_value"] == "2025-03-22"  # ISO format
        assert content["items"] == [1, 2, 3]


def test_report_result_to_stdout(capsys):
    """Test that report_result writes to stdout when output is not specified."""
    # Test data
    test_data = ResultClass(
        name="Test Result", date_value=date(2025, 3, 22), items=[1, 2, 3]
    )

    # Call report_result
    report_result(None, test_data)

    # Check that output was printed to stdout
    captured = capsys.readouterr()
    content = json.loads(captured.out)
    assert content["name"] == "Test Result"
    assert content["date_value"] == "2025-03-22"  # ISO format
    assert content["items"] == [1, 2, 3]


def test_serialize_values():
    """Test that serialize_values correctly handles dates and floats."""
    # Test date serialization
    test_date = date(2025, 3, 22)
    result = serialize_values(test_date)
    assert result == "2025-03-22"

    # Test with non-serializable value raises TypeError
    with pytest.raises(TypeError):
        serialize_values("not a date or float")


def test_validate_date():
    """Test that validate_date converts string to date object."""
    # Mock click context and param
    ctx = None
    param = None

    # Test with valid date string
    result = validate_date(ctx, param, "2025-03-22")
    assert isinstance(result, date)
    assert result.year == 2025
    assert result.month == 3
    assert result.day == 22

    # Test with None returns None
    result = validate_date(ctx, param, None)
    assert result is None


def test_convert_command_integration(fs):
    """Test that convert command works correctly with different data types."""
    grid_params = GridParams(depth=8, seed=12345, size=3)
    grid_data = Grid(
        grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        params=grid_params,
    )

    # Create a JSON file with grid data
    grid_file = "/test_grid.json"
    fs.create_file(
        grid_file,
        contents=json.dumps(
            {"grid": grid_data.grid, "params": grid_data.params},
            default=serialize_values,
        ),
    )

    # Run the convert command with grid data to stdout
    runner = CliRunner()
    result = runner.invoke(convert, ["--input", grid_file, "--kind", "grid"])

    # Check that the command completed successfully
    assert result.exit_code == 0

    # Check that the CSV output contains the expected values
    assert "0,1,2" in result.output
    assert "3,4,5" in result.output
    assert "6,7,8" in result.output
