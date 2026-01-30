"""Test person generation."""

import csv
from dataclasses import fields
from pathlib import Path
import pytest
from sqlite_utils import Database
from snailz import Parameters, Person


def test_person_creation_assigns_id():
    p = Person(family="A", personal="B")
    assert isinstance(p.ident, str)
    assert len(p.ident) == 5
    assert p.ident.startswith("P")
    assert p.ident[1:].isdigit()


def test_person_ident_cannot_be_set():
    with pytest.raises(ValueError):
        Person(ident="abc", family="A", personal="B")


def test_person_idents_are_unique(fake):
    people = Person.make(Parameters(num_persons=3), fake)
    assert len(people) == len({p.ident for p in people})


def test_person_family_is_required():
    with pytest.raises(ValueError):
        Person(family="", personal="B")


def test_person_personal_is_required():
    with pytest.raises(ValueError):
        Person(family="A", personal="")


def test_person_make_creates_supervisors(fake):
    people = Person.make(Parameters(num_persons=3), fake)
    assert len(people) == 3
    assert all(p.supervisor_id == people[-1].ident for p in people[:-1])
    assert people[-1].supervisor_id is None


def test_person_persist_to_csv(fake, tmp_path):
    persons = Person.make(Parameters(num_persons=2), fake)
    Person.save_csv(tmp_path, persons)
    with open(Path(tmp_path, f"{Person.table_name}.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 3
        assert set(rows[0]) == {"ident", "family", "personal", "supervisor_id"}


def test_person_persist_to_db(fake):
    db = Database(memory=True)
    persons = Person.make(Parameters(num_persons=3), fake)
    Person.save_db(db, persons)
    rows = list(db[Person.table_name].rows)
    assert set(r["ident"] for r in rows) == set(p.ident for p in persons)
    field_names = {f.name for f in fields(persons[0])}
    assert all(len(r) == len(field_names) for r in rows)
    assert set(rows[0].keys()) == field_names
