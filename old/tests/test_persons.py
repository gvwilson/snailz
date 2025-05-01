"""Test person generation."""

import pytest

from snailz.persons import PersonParams, Person, AllPersons


def test_generate_persons_correct_length():
    persons = AllPersons.generate(PersonParams(locale="es", number=3))
    assert len(persons.items) == 3


def test_generate_persons_fails_for_invalid_locale():
    with pytest.raises(ValueError):
        AllPersons.generate(PersonParams(locale="nope", number=3))


def test_convert_persons_to_csv():
    fixture = AllPersons(
        items=[
            Person(ident="abc", family="BC", personal="A"),
            Person(ident="def", family="EF", personal="D"),
        ]
    )
    result = fixture.to_csv()
    expected = "\n".join(["ident,personal,family", "abc,A,BC", "def,D,EF"]) + "\n"
    assert result == expected
