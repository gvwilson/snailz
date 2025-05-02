"""Test person generation."""

import csv
import io

from snailz.persons import Person


def test_generate_persons_distinct_and_correct_length():
    length = 5
    persons = Person.generate("es_MX", length)
    assert len(persons) == length
    assert len(set(p.id for p in persons)) == length
    assert len(set((p.personal, p.family) for p in persons)) == length


def test_convert_machines_to_csv():
    fixture = [
        Person(id="abc", personal="A", family="BC"),
        Person(id="def", personal="D", family="EF"),
    ]
    stream = io.StringIO()
    Person.to_csv(csv.writer(stream), fixture)
    expected = "\r\n".join(["id,family,personal", "abc,BC,A", "def,EF,D"]) + "\r\n"
    assert stream.getvalue() == expected
