"""Tests for effects module."""

from datetime import date
from snailz.effects import (
    do_all_effects,
    _do_pollution,
    _do_delay,
    _do_person,
    _do_precision,
)
from snailz.parameters import Parameters
from snailz.person import Person
from snailz.sample import Sample


def test_do_all_effects(default_params, fx_grids, fx_persons, fx_samples):
    """Test that do_all_effects returns changes dictionary."""

    changes = do_all_effects(default_params, fx_grids, fx_persons, fx_samples)
    assert isinstance(changes, dict)
    assert "daily" in changes
    assert "clumsy" in changes


def test_do_pollution_effect(fx_grids, fx_persons):
    """Test pollution effect on sample mass."""

    params = Parameters(pollution_factor=0.5)
    sample = Sample(
        id="S0001",
        grid=fx_grids[0].id,
        x=0,
        y=0,
        person=fx_persons[0].id,
        when=date(2025, 6, 15),
        mass=1.0,
    )
    fx_grids[0][0, 0] = 2

    original_mass = sample.mass
    changes = _do_pollution(params, fx_grids, fx_persons, [sample])

    # Mass should increase based on pollution
    expected_increase = params.pollution_factor * 2 * original_mass
    assert abs(sample.mass - (original_mass + expected_increase)) < 1e-10
    assert changes == {}


def test_do_delay_effect():
    """Test delay effect on sample mass."""

    params = Parameters(
        sample_date=(date(2025, 1, 1), date(2025, 1, 10)),
        sample_mass=(1.0, 2.0),
    )
    sample = Sample(
        id="S0001",
        grid="G0001",
        x=0,
        y=0,
        person="P0001",
        when=date(2025, 1, 5),  # 4 days after start
        mass=1.0,
    )

    original_mass = sample.mass
    changes = _do_delay(params, [], [], [sample])

    # Check that mass increased
    assert sample.mass > original_mass
    assert "daily" in changes
    assert changes["daily"] > 0


def test_do_person_effect():
    """Test person (clumsy) effect on sample mass."""

    params = Parameters(sample_mass=(1.0, 2.0), clumsy_factor=0.3)
    person = Person(id="P0001", family="Smith", personal="John")

    sample = Sample(
        id="S0001",
        grid="G0001",
        x=0,
        y=0,
        person=person.id,
        when=date(2025, 6, 15),
        mass=2.0,
    )

    original_mass = sample.mass
    changes = _do_person(params, [], [person], [sample])

    # Mass should decrease for clumsy person
    expected_decrease = params.sample_mass[0] * params.clumsy_factor
    assert abs(sample.mass - (original_mass - expected_decrease)) < 1e-10
    assert "clumsy" in changes
    assert changes["clumsy"] == person.id


def test_do_person_effect_clumsy_none():
    """Test person effect when clumsy_factor is None."""

    params = Parameters(sample_mass=(1.0, 2.0), clumsy_factor=None)
    person = Person(id="P0001", family="Smith", personal="John")

    sample = Sample(
        id="S0001",
        grid="G0001",
        x=0,
        y=0,
        person=person.id,
        when=date(2025, 6, 15),
        mass=2.0,
    )

    original_mass = sample.mass
    changes = _do_person(params, [], [person], [sample])

    assert sample.mass == original_mass
    assert changes == {}


def test_do_precision_effect():
    """Test precision rounding effect."""

    params = Parameters(precision=2)

    sample = Sample(
        id="S0001",
        grid="G0001",
        x=0,
        y=0,
        person="P0001",
        when=date(2025, 6, 15),
        mass=1.23456789,
    )

    changes = _do_precision(params, [], [], [sample])

    # Mass should be rounded to 2 decimal places
    assert sample.mass == 1.23
    assert changes == {}


def test_effects_order_matters(default_params, fx_grids, fx_persons):
    """Test that effects are applied in the correct order."""

    # Create sample with known initial conditions
    sample = Sample(
        id="S0001",
        grid=fx_grids[0].id,
        x=0,
        y=0,
        person=fx_persons[0].id,
        when=default_params.sample_date[0],
        mass=1.0,
    )

    # Set pollution value
    fx_grids[0][0, 0] = 1

    # Apply all effects
    do_all_effects(default_params, fx_grids, fx_persons, [sample])

    # Verify that mass was modified and precision was applied last
    assert isinstance(sample.mass, float)
    # Mass should be rounded to default precision (2 decimal places)
    assert sample.mass == round(sample.mass, default_params.precision)
