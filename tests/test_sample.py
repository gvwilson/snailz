"""Tests for sample module."""

from datetime import date

import pytest

from snailz.sample import Sample


def test_sample_creation(default_params, fx_grids, fx_persons):
    """Test sample creation with default parameters."""

    sample = Sample.make(default_params, fx_grids, fx_persons)[0]
    assert sample.sample_id.startswith("S")
    assert len(sample.sample_id) == 5  # S + 4 digits
    assert sample.grid_id in [g.grid_id for g in fx_grids]
    assert sample.person_id in [p.person_id for p in fx_persons]
    assert sample.pollution >= 0
    assert (
        default_params.sample_date[0]
        <= sample.timestamp
        <= default_params.sample_date[1]
    )
    assert default_params.sample_mass[0] <= sample.mass <= default_params.sample_mass[1]


@pytest.mark.parametrize(
    "changed",
    [
        {"id": ""},
        {"grid": ""},
        {"x": -1},
        {"y": -1},
        {"pollution": -1},
        {"mass": 0},
        {"mass": -1},
    ],
)
def test_sample_parameter_validation(changed):
    """Test invalid sample parameters are rejected."""

    values = {
        "id": "",
        "grid": "G0001",
        "x": 5,
        "y": 3,
        "pollution": 10,
        "person": "P0001",
        "when": date(2025, 6, 15),
        "mass": 1.23,
        **changed,
    }
    with pytest.raises(ValueError):
        Sample(**values)


def test_sample_unique_ids(default_params, fx_grids, fx_persons):
    """Test that samples get unique IDs."""

    samples = Sample.make(default_params, fx_grids, fx_persons)
    assert samples[0].sample_id != samples[1].sample_id


def test_sample_id_format(default_params, fx_grids, fx_persons):
    """Test sample ID format is consistent."""

    sample = Sample.make(default_params, fx_grids, fx_persons)[0]
    assert sample.sample_id[0] == "S"
    assert sample.sample_id[1:].isdigit()
    assert len(sample.sample_id[1:]) == 4
