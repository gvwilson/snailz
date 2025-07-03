"""Tests for utils module."""

from datetime import date
from io import StringIO
import json
import random
import pytest
from unittest.mock import patch

from snailz.utils import (
    json_dump,
    random_date,
    random_mass,
    file_or_std,
    _serialize_json,
)
from snailz.parameters import Parameters
from snailz.person import Person


def test_random_date():
    """Test random date generation within range."""

    params = Parameters(sample_date=(date(2025, 1, 1), date(2025, 1, 10)))

    random.seed(123)
    for _ in range(100):
        random_dt = random_date(params)
        assert params.sample_date[0] <= random_dt <= params.sample_date[1]


def test_random_mass():
    """Test random mass generation within range."""

    params = Parameters(sample_mass=(0.5, 2.0))
    random.seed(123)
    for _ in range(100):
        mass = random_mass(params)
        assert params.sample_mass[0] <= mass <= params.sample_mass[1]


def test_json_dump_with_date():
    """Test JSON dump with date serialization."""

    data = {"date": date(2025, 6, 15)}
    result = json_dump(data)
    parsed = json.loads(result)
    assert parsed == {"date": "2025-06-15"}


def test_json_dump_with_basemodel():
    """Test JSON dump with BaseModel serialization."""

    person = Person(id="P0001", family="Smith", personal="John")
    data = {"person": person}
    result = json_dump(data)
    parsed = json.loads(result)
    assert parsed == {"person": {"id": "P0001", "family": "Smith", "personal": "John"}}


def test_serialize_json_unsupported_type():
    """Test JSON serialization raises error for unsupported types."""

    with pytest.raises(TypeError, match="Type .* not serializable"):
        _serialize_json({1, 2, 3})


def test_file_or_std_with_file(tmp_path):
    """Test file_or_std context manager with actual file."""

    test_file = tmp_path / "test.txt"
    test_content = "Hello, World!"
    with file_or_std(tmp_path, "test.txt", "w") as f:
        f.write(test_content)
    assert test_file.read_text() == test_content


def test_file_or_std_with_stdout():
    """Test file_or_std context manager with stdout."""

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        with file_or_std(None, "dummy.txt", "w") as f:
            f.write("test output")
        assert mock_stdout.getvalue() == "test output"


def test_file_or_std_with_stdin():
    """Test file_or_std context manager with stdin."""

    test_input = "test input"
    with patch("sys.stdin", StringIO(test_input)):
        with file_or_std(None, "dummy.txt", "r") as f:
            content = f.read()
        assert content == test_input


def test_file_or_std_invalid_mode():
    """Test file_or_std with invalid mode raises error."""

    with pytest.raises(ValueError, match="bad filename/mode"):
        with file_or_std(None, "test.txt", "x"):
            pass
