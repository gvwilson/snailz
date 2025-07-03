"""Tests for person module."""

import pytest
from snailz.person import Person
from snailz.parameters import Parameters


def test_person_creation(default_params):
    """Test person creation with default parameters."""

    person = Person.make(default_params)
    assert person.id.startswith("P")
    assert len(person.id) == 5  # P + 4 digits
    assert len(person.family) > 0
    assert len(person.personal) > 0


def test_person_empty_id_validation():
    """Test empty ID validation fails."""

    with pytest.raises(ValueError):
        Person(id="", family="Smith", personal="John")


def test_person_empty_family_validation():
    """Test empty family name validation fails."""

    with pytest.raises(ValueError):
        Person(id="P0001", family="", personal="John")


def test_person_empty_personal_validation():
    """Test empty personal name validation fails."""

    with pytest.raises(ValueError):
        Person(id="P0001", family="Smith", personal="")


def test_person_csv_header():
    """Test CSV header generation."""

    header = Person.csv_header()
    assert header == "id,family,personal"


def test_person_csv_output():
    """Test CSV string output."""

    person = Person(id="P0001", family="Smith", personal="John")
    csv_output = str(person)
    assert csv_output == "P0001,Smith,John"


def test_person_unique_ids(default_params):
    """Test that persons get unique IDs."""

    num_persons = 100
    ids = {Person.make(default_params).id for _ in range(num_persons)}
    assert len(ids) == num_persons


def test_person_with_custom_locale():
    """Test person creation with custom locale."""

    params = Parameters(locale="en_US")
    person = Person.make(params)
    assert len(person.family) > 0
    assert len(person.personal) > 0
