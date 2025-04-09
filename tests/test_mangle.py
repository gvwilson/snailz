"""Test database creation."""

import csv

from pathlib import Path

import pytest

from snailz.assays import NUM_ASSAY_HEADER_ROWS
from snailz.mangle import mangle_assays
from snailz.persons import Person, AllPersons

ORIGINAL = "/test_readings.csv"
MANGLED = "/test_raw.csv"

READING = """\
id,123456,,,
specimen,ABCDEF,,,
date,2024-02-01,,,
by,ab1234,,,
machine,M0001,,,
,A,B,C,D
1,1.0,2.0,3.0,4.0
2,11.0,12.0,13.0,14.0
3,21.0,22.0,23.0,24.0
4,31.0,32.0,33.0,34.0
"""

PERSONS = AllPersons(
    items=[
        Person(ident="ab1234", family="BCD", personal="A"),
    ]
)


def _check_id(rows):
    id_row = [r for r in rows if r[0] == "id"]
    assert len(id_row) == 1
    assert id_row[0][1] == "'123456'"


def _check_indent(rows):
    assert all(r[0] == "" for r in rows[NUM_ASSAY_HEADER_ROWS:])


def _check_person(rows):
    assert not any(r[0] == "by" for r in rows)
    person_row = [r for r in rows if r[0] == "performed"]
    assert len(person_row) == 1
    assert person_row[0][1] == "A BCD"


@pytest.mark.parametrize(
    "op", [("id", _check_id), ("indent", _check_indent), ("person", _check_person)]
)
def test_mangle_single_assay(fs, op):
    name, check_func = op
    fs.create_file(ORIGINAL, contents=READING)
    mangle_assays("/", PERSONS, forced=[name])
    with open(MANGLED, "r") as stream:
        check_func([r for r in csv.reader(stream)])


def test_mangle_all_assays(fs):
    num_assays = 10
    for i in range(num_assays):
        fs.create_file(f"/{i:06}_readings.csv", contents=READING)
    mangle_assays("/", PERSONS)
    matches = list(Path("/").glob("*_raw.csv"))
    assert len(matches) == num_assays
