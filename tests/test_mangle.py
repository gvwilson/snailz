"""Test mangle functionality."""

import json
import pytest
from unittest.mock import mock_open, patch

from snailz.mangle import (
    mangle_assays,
    _load_people,
    _mangle_assay,
    _mangle_id,
    _mangle_indent,
    _mangle_person,
)

# Sample data for testing
SAMPLE_PEOPLE_DATA = {
    "individuals": [
        {"ident": "abc123", "personal": "John", "family": "Doe"},
        {"ident": "def456", "personal": "Jane", "family": "Smith"},
    ]
}

SAMPLE_ASSAY_DATA = [
    ["id", "12345"],
    ["specimen", "AB789"],
    ["performed", "2023-05-15"],
    ["performed_by", "abc123"],
    ["", "A", "B", "C"],
    ["1", "S", "C", "S"],
    ["2", "C", "S", "C"],
    ["3", "S", "C", "S"],
]


def test_load_people():
    """Test loading people data."""
    with patch("builtins.open", mock_open(read_data=json.dumps(SAMPLE_PEOPLE_DATA))):
        result = _load_people("fake_path.json")

    assert len(result) == 2
    assert "abc123" in result
    assert "def456" in result
    assert result["abc123"]["personal"] == "John"
    assert result["def456"]["family"] == "Smith"


def test_load_people_error():
    """Test error handling when loading people data."""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with pytest.raises(ValueError, match="Error loading people data"):
            _load_people("fake_path.json")


def test_mangle_id():
    """Test mangling ID field."""
    data = [row[:] for row in SAMPLE_ASSAY_DATA]
    result = _mangle_id(data, {})
    assert result[0][1] == "'12345'"
    assert result[1][1] == "AB789"


def test_mangle_indent():
    """Test indenting numeric rows."""
    data = [row[:] for row in SAMPLE_ASSAY_DATA]
    result = _mangle_indent(data, {})

    # Check metadata rows have empty padding at end
    for i in range(5):
        assert result[i][-1] == ""
        assert result[i][0] == data[i][0]

    # Check data rows have empty padding at start
    for i in range(5, 8):
        assert result[i][0] == ""
        assert result[i][1] == data[i][0]


def test_mangle_person():
    """Test replacing person ID with name."""
    data = [row[:] for row in SAMPLE_ASSAY_DATA]
    people = {
        "abc123": {"personal": "John", "family": "Doe"},
        "def456": {"personal": "Jane", "family": "Smith"},
    }

    result = _mangle_person(data, people)
    assert result[3][1] == "John Doe"
    assert result[0][1] == "12345"
    assert result[1][1] == "AB789"


def test_mangle_assay():
    """Test the mangle_assay function that applies random manglers."""
    data = [row[:] for row in SAMPLE_ASSAY_DATA]  # Make a copy
    people = {
        "abc123": {"personal": "John", "family": "Doe"},
        "def456": {"personal": "Jane", "family": "Smith"},
    }

    with (
        patch("random.randint", return_value=2),
        patch("random.sample", return_value=[_mangle_id, _mangle_person]),
    ):
        result = _mangle_assay(people, data)

    assert result[0][1] == "'12345'"  # ID mangled
    assert result[3][1] == "John Doe"  # Person mangled


def test_mangle_assays(fs):
    """Test the main mangle_assays function using pyfakefs."""
    # Fake assays
    assays_dir = "/assays_dir"
    fs.create_dir(assays_dir)
    assay_files = ["file1_assay.csv", "file2_assay.csv"]
    for file in assay_files:
        assay_content = "\n".join(",".join(row) for row in SAMPLE_ASSAY_DATA)
        fs.create_file(f"{assays_dir}/{file}", contents=assay_content)

    # Fake people
    people_file = "/people.json"
    fs.create_file(people_file, contents=json.dumps(SAMPLE_PEOPLE_DATA))

    mangle_assays(assays_dir, people_file)
    raw_files = [f.replace("_assay.csv", "_raw.csv") for f in assay_files]
    for raw in raw_files:
        path = f"{assays_dir}/{raw}"
        assert fs.exists(path)
        with open(path, "r") as reader:
            content = reader.read()
            assert content
