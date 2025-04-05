"""Test assay generation."""

from datetime import date
import pytest

from snailz.assays import AssayParams, Assay, AllAssays, assays_generate
from snailz.grids import Point
from snailz.persons import Person, AllPersons
from snailz.specimens import Specimen, AllSpecimens


PERSONS = AllPersons(
    items=[
        Person(ident="abc", family="BC", personal="A"),
        Person(ident="def", family="EF", personal="D"),
    ]
)

SPECIMENS = AllSpecimens(
    loci=[1],
    reference="AAAA",
    susc_base="C",
    susc_locus=0,
    items=[
        Specimen(
            ident="S01",
            grid_id="G01",
            collected=date(2023, 7, 5),
            genome="ACGT",
            location=Point(x=1, y=1),
            mass=0.1,
        ),
        Specimen(
            ident="S03",
            grid_id="G03",
            collected=date(2024, 7, 5),
            genome="TGCA",
            location=Point(x=3, y=3),
            mass=0.3,
        ),
    ],
)


def test_generate_assays_correct_length_and_reference_ids():
    assays = assays_generate(AssayParams(), PERSONS, SPECIMENS)
    assert len(assays.items) == 2
    for a, s in zip(assays.items, SPECIMENS.items):
        assert a.specimen == s.ident
    person_ids = {p.ident for p in PERSONS.items}
    assert all(a.person in person_ids for a in assays.items)


def test_assay_csv_fails_for_unknown_kind():
    assays = assays_generate(AssayParams(), PERSONS, SPECIMENS)
    with pytest.raises(ValueError):
        assays.items[0].to_csv("nope")


def test_convert_assays_to_csv():
    first = Assay(
        ident="a01",
        specimen="s01",
        person="p01",
        performed=date(2021, 7, 1),
        readings=[[1.0, 2.0], [3.0, 4.0]],
        treatments=[["C", "S"], ["C", "S"]],
    )
    fixture = AllAssays(
        items=[
            first,
            Assay(
                ident="a02",
                specimen="s02",
                person="p02",
                performed=date(2021, 7, 11),
                readings=[[10.0, 20.0], [30.0, 40.0]],
                treatments=[["S", "S"], ["C", "C"]],
            ),
        ]
    )
    expected = [
        "ident,specimen,person,performed",
        "a01,s01,p01,2021-07-01",
        "a02,s02,p02,2021-07-11",
    ]
    assert fixture.to_csv() == "\n".join(expected) + "\n"

    readings = [
        "id,a01,",
        "specimen,s01,",
        "date,2021-07-01,",
        "by,p01,",
        ",A,B",
        "1,1.0,2.0",
        "2,3.0,4.0",
    ]
    assert first.to_csv("readings") == "\n".join(readings) + "\n"

    treatments = [
        "id,a01,",
        "specimen,s01,",
        "date,2021-07-01,",
        "by,p01,",
        ",A,B",
        "1,C,S",
        "2,C,S",
    ]
    assert first.to_csv("treatments") == "\n".join(treatments) + "\n"
