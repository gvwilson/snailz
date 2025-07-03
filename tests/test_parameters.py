"""Tests for parameters module."""

from datetime import date

import pytest

from snailz.parameters import Parameters


def test_custom_parameters():
    """Test custom parameter values."""

    params = Parameters(seed=42, precision=3, num_persons=10, locale="en_US")
    assert params.seed == 42
    assert params.precision == 3
    assert params.num_persons == 10
    assert params.locale == "en_US"


@pytest.mark.parametrize(
    "name,value",
    [
        ["locale", "invalid"],
        ["sample_mass", (2.0, 1.0)],
        ["sample_date", (date(2025, 12, 31), date(2025, 1, 1))],
        ["clumsy_factor", -0.5],
    ],
)
def test_invalid_parameter_values(name, value):
    """Test invalid parameter values raise error."""

    with pytest.raises(ValueError):
        Parameters(**{name: value})
