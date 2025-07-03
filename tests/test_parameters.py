"""Tests for parameters module."""

import pytest
from datetime import date
from snailz.parameters import Parameters


def test_default_parameters():
    """Test default parameter values."""
    params = Parameters()
    assert params.seed == 123456
    assert params.precision == 2
    assert params.num_persons == 5
    assert params.num_grids == 3
    assert params.num_samples == 20
    assert params.locale == "et_EE"
    assert params.grid_size == 11
    assert params.sample_mass_min == 0.5
    assert params.sample_mass_max == 1.5
    assert params.sample_date_min == date(2025, 1, 1)
    assert params.sample_date_max == date(2025, 3, 31)
    assert params.pollution_factor == 0.3
    assert params.clumsy_factor == 0.5


def test_custom_parameters():
    """Test custom parameter values."""
    params = Parameters(seed=42, precision=3, num_persons=10, locale="en_US")
    assert params.seed == 42
    assert params.precision == 3
    assert params.num_persons == 10
    assert params.locale == "en_US"


def test_invalid_locale():
    """Test invalid locale raises error."""
    with pytest.raises(ValueError, match="unknown locale"):
        Parameters(locale="invalid_locale")


def test_invalid_sample_mass_range():
    """Test invalid sample mass range raises error."""
    with pytest.raises(ValueError, match="invalid sample size limits"):
        Parameters(sample_mass_min=2.0, sample_mass_max=1.0)


def test_invalid_sample_date_range():
    """Test invalid sample date range raises error."""
    with pytest.raises(ValueError, match="invalid sample date limits"):
        Parameters(sample_date_min=date(2025, 12, 31), sample_date_max=date(2025, 1, 1))
