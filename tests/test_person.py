"""Tests for person module."""

import pytest
from snailz.person import Person
from snailz.parameters import Parameters


def test_person_creation(default_params):
    """Test person creation with default parameters."""

    person = Person.make(default_params)[0]
    assert person.person_id.startswith("P")
    assert len(person.person_id) == 5  # P + 4 digits
    assert len(person.family) > 0
    assert len(person.personal) > 0


def test_person_empty_id_validation():
    """Test empty ID validation fails."""

    with pytest.raises(ValueError):
        Person(person_id="", family="Smith", personal="John")


def test_person_empty_family_validation():
    """Test empty family name validation fails."""

    with pytest.raises(ValueError):
        Person(person_id="P0001", family="", personal="John")


def test_person_empty_personal_validation():
    """Test empty personal name validation fails."""

    with pytest.raises(ValueError):
        Person(person_id="P0001", family="Smith", personal="")


def test_person_csv_output():
    """Test CSV string output."""

    person = Person(person_id="P0001", family="Smith", personal="John")
    csv_output = str(person)
    assert csv_output == "P0001,Smith,John"


def test_person_unique_ids(default_params):
    """Test that persons get unique IDs."""

    num_persons = 100
    default_params.num_persons = num_persons
    person_ids = {p.person_id for p in Person.make(default_params)}
    assert len(person_ids) == num_persons


def test_person_with_custom_locale():
    """Test person creation with custom locale."""

    params = Parameters(locale="en_US")
    persons = Person.make(params)
    assert all(len(p.family) > 0 for p in persons)
    assert all(len(p.personal) > 0 for p in persons)
