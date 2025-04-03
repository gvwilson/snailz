"""Test person generation."""

from pathlib import Path
import pytest

from snailz.persons import PersonParams, Person, PersonList, persons_generate


def test_generate_persons_correct_length():
    persons = persons_generate(PersonParams(locale="es", number=3))
    assert len(persons.persons) == 3


def test_generate_persons_fails_for_invalid_locale():
    with pytest.raises(ValueError):
        persons_generate(PersonParams(locale="nope", number=3))


def test_convert_persons_to_csv():
    fixture = PersonList(
        persons=[
            Person(ident="abc", family="BC", personal="A"),
            Person(ident="def", family="EF", personal="D"),
        ]
    )
    result = fixture.to_csv()
    expected = "\n".join([
        "ident,personal,family",
        "abc,A,BC",
        "def,D,EF"
    ]) + "\n"
    assert result == expected
