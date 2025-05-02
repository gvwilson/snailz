"""Test database creation."""

import csv
from unittest.mock import patch

import pytest

from snailz.mangle import mangle_assay
from snailz.persons import Person

ORIGINAL = "/test_readings.csv"
MANGLED = "/test_raw.csv"

READINGS = """\
id,A0001
specimen,S0001
machine,M00
person,P05
performed,2025-04-08
,A,B,C,D
1,1.5,0.53,0.4,0.12
2,0.28,1.57,1.56,0.36
3,0.47,0.41,0.56,0.33
4,0.06,0.03,0.85,1.58
"""

NUM_ASSAY_HEADER_ROWS = 5

PERSONS = [
    Person(id="P05", family="BCD", personal="A"),
]


def _check_id(rows):
    id_row = [r for r in rows if r[0] == "id"]
    assert len(id_row) == 1
    assert id_row[0][1] == "'A0001'"


def _check_indent(rows):
    assert all(r[0] == "" for r in rows[NUM_ASSAY_HEADER_ROWS:])


def _check_missing(rows):
    assert not any([r[0] == "machine" for r in rows])


def _check_person(rows):
    person_row = [r for r in rows if r[0] == "by"]
    assert len(person_row) == 1
    assert person_row[0][1] == "A BCD"


def test_no_mangles_has_no_effect(fs):
    fs.create_file(ORIGINAL, contents=READINGS)
    with patch("random.randint", return_value=0):
        mangle_assay(ORIGINAL, MANGLED, PERSONS)
    with open(MANGLED, "r") as reader:
        assert reader.read() == READINGS


@pytest.mark.parametrize(
    "op",
    [
        ("id", _check_id),
        ("indent", _check_indent),
        ("missing", _check_missing),
        ("person", _check_person),
    ],
)
def test_mangle_single_assay(fs, op):
    name, check_func = op
    fs.create_file(ORIGINAL, contents=READINGS)
    mangle_assay(ORIGINAL, MANGLED, PERSONS, forced=[name])
    with open(MANGLED, "r") as stream:
        check_func([r for r in csv.reader(stream)])
