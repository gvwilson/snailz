"""Test assay generation."""

from datetime import date
import pytest
import random

from snailz.assays import AssayParams, Assay, AllAssays
from snailz.machines import Machine, AllMachines
from snailz.grid import Grid, Point
from snailz.persons import Person, AllPersons
from snailz.specimens import Specimen, AllSpecimens

MACHINE_ID = "E1234"
MACHINES_1 = AllMachines(
    items=[Machine(ident=MACHINE_ID, name="SomeMachine", brightness=0.95)]
)

PERSONS_1 = AllPersons(items=[Person(ident="abc", family="BC", personal="A")])

SPECIMENS_1 = AllSpecimens(
    loci=[0],
    reference="A",
    susc_base="A",
    susc_locus=0,
    items=[
        Specimen(
            ident="S01",
            survey_id="G01",
            collected=date(2023, 7, 5),
            genome="ACGT",
            location=Point(x=1, y=1),
            mass=0.1,
            is_mutant=False,
        ),
    ],
)

PERSONS_2 = AllPersons(
    items=[
        Person(ident="abc", family="BC", personal="A"),
        Person(ident="def", family="EF", personal="D"),
    ]
)

SPECIMENS_2 = AllSpecimens(
    loci=[1],
    reference="AAAA",
    susc_base="C",
    susc_locus=0,
    items=[
        Specimen(
            ident="S01",
            survey_id="G01",
            collected=date(2023, 7, 5),
            genome="ACGT",
            location=Point(x=1, y=1),
            mass=0.1,
        ),
        Specimen(
            ident="S03",
            survey_id="G03",
            collected=date(2024, 7, 5),
            genome="TGCA",
            location=Point(x=3, y=3),
            mass=0.3,
        ),
    ],
)


def test_assay_parameter_validation():
    with pytest.raises(ValueError):
        AssayParams(
            baseline=10.0,
            mutant=0.1,
        )


def test_assay_explicit_treatments_and_readings():
    treatments = Grid[str](width=2, height=2, default="", data=[["C", "S"], ["C", "S"]])
    readings = Grid[float](
        width=2, height=2, default=0.0, data=[[1.0, 2.0], [3.0, 4.0]]
    )
    assay = Assay(
        ident="a01",
        specimen="s01",
        person="p01",
        machine=MACHINE_ID,
        performed=date(2021, 7, 1),
        treatments=treatments,
        readings=readings,
    )
    assert assay.treatments[0, 0] == "C"
    assert assay.treatments[0, 1] == "S"
    assert assay.treatments[1, 0] == "C"
    assert assay.treatments[1, 1] == "S"
    assert assay.readings[0, 0] == 1.0
    assert assay.readings[0, 1] == 2.0
    assert assay.readings[1, 0] == 3.0
    assert assay.readings[1, 1] == 4.0


def test_generate_assays_correct_length_and_reference_ids():
    params = AssayParams().model_copy(update={"p_duplicate_assay": 0.0})
    assays = AllAssays.generate(params, PERSONS_2, MACHINES_1, SPECIMENS_2)
    assert len(assays.items) == 2
    assert {a.specimen for a in assays.items} == {s.ident for s in SPECIMENS_2.items}
    person_ids = {p.ident for p in PERSONS_2.items}
    assert all(a.person in person_ids for a in assays.items)


def test_generate_assays_multiple_assays_per_specimen():
    params = AssayParams().model_copy(update={"p_duplicate_assay": 1.0})
    assays = AllAssays.generate(params, PERSONS_2, MACHINES_1, SPECIMENS_2)
    assert len(assays.items) == 2 * len(SPECIMENS_2.items)


def test_assay_csv_fails_for_unknown_kind():
    assays = AllAssays.generate(AssayParams(), PERSONS_2, MACHINES_1, SPECIMENS_2)
    with pytest.raises(ValueError):
        assays.items[0].to_csv("nope")


def test_convert_assays_to_csv():
    first = Assay(
        ident="a01",
        specimen="s01",
        person="p01",
        machine=MACHINE_ID,
        performed=date(2021, 7, 1),
        treatments=Grid[str](
            width=2, height=2, default="", data=[["C", "S"], ["C", "S"]]
        ),
        readings=Grid[float](
            width=2, height=2, default=0.0, data=[[1.0, 2.0], [3.0, 4.0]]
        ),
    )
    second = Assay(
        ident="a02",
        specimen="s02",
        person="p02",
        machine=MACHINE_ID,
        performed=date(2021, 7, 11),
        treatments=Grid[str](
            width=2, height=2, default="", data=[["C", "C"], ["S", "S"]]
        ),
        readings=Grid[float](
            width=2, height=2, default=0.0, data=[[10.0, 20.0], [30.0, 40.0]]
        ),
    )
    fixture = AllAssays(items=[first, second])
    expected = [
        "ident,specimen,person,performed,machine",
        "a01,s01,p01,2021-07-01,E1234",
        "a02,s02,p02,2021-07-11,E1234",
    ]
    assert fixture.to_csv() == "\n".join(expected) + "\n"

    treatments = [
        "id,a01,",
        "specimen,s01,",
        "date,2021-07-01,",
        "by,p01,",
        "machine,E1234,",
        ",A,B",
        "1,S,S",
        "2,C,C",
    ]
    assert first.to_csv("treatments") == "\n".join(treatments) + "\n"

    readings = [
        "id,a01,",
        "specimen,s01,",
        "date,2021-07-01,",
        "by,p01,",
        "machine,E1234,",
        ",A,B",
        "1,2.0,4.0",
        "2,1.0,3.0",
    ]
    assert first.to_csv("readings") == "\n".join(readings) + "\n"


@pytest.mark.parametrize("seed", [128915, 45729, 495924, 152741, 931866])
def test_assay_reading_value_susceptible(seed):
    random.seed(seed)
    params = AssayParams().model_copy(update={"plate_size": 2, "degrade": 0.0})

    specimens = SPECIMENS_1.model_copy()
    specimens.items = [specimens.items[0].model_copy(update={"is_mutant": True})]
    assert specimens.items[0].is_mutant

    assays = AllAssays.generate(params, PERSONS_1, MACHINES_1, specimens)
    assay = assays.items[0]
    for x in range(2):
        for y in range(2):
            if assay.treatments[x, y] == "C":
                assert 0.0 <= assay.readings[x, y] <= 3.0
            else:
                assert 2.0 <= assay.readings[x, y] <= 8.0


@pytest.mark.parametrize("seed", [127891, 457129, 9924, 527411, 931866])
def test_assay_reading_value_not_susceptible(seed):
    random.seed(seed)
    params = AssayParams().model_copy(update={"plate_size": 2, "degrade": 0.0})

    specimens = SPECIMENS_1.model_copy()
    specimens.items = [specimens.items[0].model_copy(update={"is_mutant": False})]
    assert not specimens.items[0].is_mutant

    assays = AllAssays.generate(params, PERSONS_1, MACHINES_1, specimens)
    assay = assays.items[0]
    for x in range(2):
        for y in range(2):
            if assay.treatments[x, y] == "C":
                assert 0.0 <= assay.readings[x, y] <= 3.0
            else:
                assert 0.0 < assay.readings[x, y] <= 5.0
