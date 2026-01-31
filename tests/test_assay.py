"""Test assay construction."""

import csv
from dataclasses import fields
from pathlib import Path
from sqlite_utils import Database

from snailz import Assay, Grid, Machine, Parameters, Person, Rating


def test_assay_id_set_correctly():
    ident = Assay().ident
    assert ident.startswith("A")
    assert len(ident) == 5


def test_assay_random_contents_size_and_balance():
    contents = Assay._random_contents(Parameters(assay_size=6))
    assert len(contents) == 6
    assert contents.count("C") == 3
    assert contents.count("T") == 3


def test_assay_random_readings_length_and_precision():
    contents = "CTTC"
    readings = Assay._random_readings(Parameters(), contents, 10.0, True)
    assert len(readings) == len(contents)
    assert all(isinstance(r, float) for r in readings)


def test_assay_assay_readings_long_format():
    a = Assay(contents="CT", readings=[1.1, 2.2])
    rows = Assay._assay_readings([a])
    assert rows == [
        {"assay_id": a.ident, "contents": "C", "reading": 1.1},
        {"assay_id": a.ident, "contents": "T", "reading": 2.2},
    ]


def test_assay_make_creates_assays():
    params = Parameters(num_assays=2)
    grid = Grid(size=1, spacing=1.0, params=params)
    rating = Rating(person_id="P1", machine_id="M1", certified=False)
    assays = Assay.make(params, [grid], [rating])
    assert len(assays) == 2
    for a in assays:
        assert a.person_id == "P1"
        assert a.machine_id == "M1"
        assert all(c in "CT" for c in a.contents)
        assert all(r >= 0.0 for r in a.readings)


def test_assay_persist_to_csv(tmp_path):
    params = Parameters(num_assays=2, assay_size=3)
    grid = Grid(size=1, spacing=1.0, params=params)
    rating = Rating(person_id="P1", machine_id="M1", certified=False)
    assays = Assay.make(params, [grid], [rating])
    Assay.save_csv(tmp_path, assays)

    with open(Path(tmp_path, f"{Assay.table_name}.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 3

    with open(Path(tmp_path, "assay_readings.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 7


def test_assay_persist_to_db():
    db = Database(memory=True)
    params = Parameters(num_assays=2)
    grid = Grid(size=1, spacing=1.0, params=params)
    persons = [Person(family="A", personal="B")]
    machines = [Machine(name="M1")]
    rating = Rating(
        person_id=persons[0].ident, machine_id=machines[0].ident, certified=True
    )
    assays = Assay.make(params, [grid], [rating])

    Person.save_db(db, persons)
    Machine.save_db(db, machines)
    Assay.save_db(db, assays)

    rows = list(db[Assay.table_name].rows)
    assert set(r["ident"] for r in rows) == set(a.ident for a in assays)
    field_names = {f.name for f in fields(assays[0])}
    assert set(rows[0].keys()).issubset(field_names)
