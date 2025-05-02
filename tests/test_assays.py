"""Test assay functionality."""

import csv
from datetime import date
import io
import random

from snailz.assays import Assay
from snailz.grid import Grid
from snailz.machines import Machine
from snailz.params import AssayParams
from snailz.persons import Person
from snailz.specimens import Specimen


def test_assay_treatment_grid_generation():
    random.seed(42)
    params = AssayParams(plate_size=3)

    # Test the internal method directly
    grid = Assay._make_treatments(params)
    assert grid.size == 3
    for x in range(grid.size):
        for y in range(grid.size):
            assert grid[x, y] in {"C", "S"}

    # Make sure we have at least one of each type
    has_control = False
    has_specimen = False
    for x in range(grid.size):
        for y in range(grid.size):
            if grid[x, y] == "C":
                has_control = True
            if grid[x, y] == "S":
                has_specimen = True

    assert has_control
    assert has_specimen


def test_assay_reading_grid_generation():
    random.seed(42)
    params = AssayParams(
        plate_size=3,
        mean_control=0.0,
        mean_normal=2.0,
        mean_mutant=5.0,
        reading_noise=0.5,
    )

    # Create a test specimen
    specimen = Specimen(
        id="S0001", genome="ACGT", is_mutant=False, mass=10.0, sampled=date(2025, 1, 1)
    )

    # Create a treatment grid
    treatments = Grid(size=3)
    treatments[0, 0] = "C"
    treatments[0, 1] = "C"
    treatments[0, 2] = "S"
    treatments[1, 0] = "S"
    treatments[1, 1] = "S"
    treatments[1, 2] = "C"
    treatments[2, 0] = "S"
    treatments[2, 1] = "C"
    treatments[2, 2] = "S"

    # Test the internal method directly
    readings = Assay._make_readings(params, specimen, treatments)

    assert readings.size == 3

    # Verify control readings are near 0
    for x in range(readings.size):
        for y in range(readings.size):
            if treatments[x, y] == "C":
                assert 0 <= readings[x, y] <= 1.5  # allowing for some noise
            else:
                # Non-mutant specimen readings
                assert 0.5 <= readings[x, y] <= 3.5  # allowing for noise


def test_assay_generation():
    random.seed(42)
    params = AssayParams()

    # Create minimal test objects
    specimen = Specimen(
        id="S0001", genome="ACGT", is_mutant=True, mass=10.0, sampled=date(2025, 1, 1)
    )

    # Create real Machine and Person objects
    machine = Machine(id="M0001", name="Test Machine")
    person = Person(id="P0001", family="Doe", personal="Jane")

    # Generate an assay
    assay = Assay.generate(params, specimen, machine, person)

    assert assay.id.startswith("A")
    assert assay.specimen_id == "S0001"
    assert assay.machine_id == "M0001"
    assert assay.person_id == "P0001"
    assert assay.performed > specimen.sampled
    assert assay.treatments.size == params.plate_size
    assert assay.readings.size == params.plate_size


def test_assay_csv_export():
    treatments = Grid(size=2)
    treatments[0, 0] = "C"
    treatments[0, 1] = "S"
    treatments[1, 0] = "S"
    treatments[1, 1] = "C"

    readings = Grid(size=2)
    readings[0, 0] = 0.5
    readings[0, 1] = 2.5
    readings[1, 0] = 3.5
    readings[1, 1] = 1.0

    assay = Assay(
        id="A0001",
        specimen_id="S0001",
        machine_id="M0001",
        person_id="P0001",
        performed=date(2025, 1, 1),
        treatments=treatments,
        readings=readings,
    )

    # Test treatment export
    treatment_output = io.StringIO()
    writer = csv.writer(treatment_output)
    assay.to_csv(writer, write_treatments=True)

    result = treatment_output.getvalue().strip().split("\n")
    assert len(result) >= 7
    assert "id,A0001" in result[0]
    assert "specimen,S0001" in result[1]

    # Test readings export
    readings_output = io.StringIO()
    writer = csv.writer(readings_output)
    assay.to_csv(writer, write_treatments=False)

    result = readings_output.getvalue().strip().split("\n")
    assert len(result) >= 7
    assert "id,A0001" in result[0]
    assert "specimen,S0001" in result[1]


def test_all_assays_csv_export():
    assay1 = Assay(
        id="A0001",
        specimen_id="S0001",
        machine_id="M0001",
        person_id="P0001",
        performed=date(2025, 1, 1),
        treatments=Grid(size=2),
        readings=Grid(size=2),
    )

    assay2 = Assay(
        id="A0002",
        specimen_id="S0002",
        machine_id="M0002",
        person_id="P0002",
        performed=date(2025, 1, 2),
        treatments=Grid(size=2),
        readings=Grid(size=2),
    )

    # Set specific values for grids
    assay1.treatments[0, 0] = "C"
    assay1.treatments[0, 1] = "S"
    assay1.treatments[1, 0] = "S"
    assay1.treatments[1, 1] = "C"
    assay1.readings[0, 0] = 0.5
    assay1.readings[0, 1] = 2.5
    assay1.readings[1, 0] = 3.5
    assay1.readings[1, 1] = 1.0

    assay2.treatments[0, 0] = "S"
    assay2.treatments[0, 1] = "C"
    assay2.treatments[1, 0] = "C"
    assay2.treatments[1, 1] = "S"
    assay2.readings[0, 0] = 4.0
    assay2.readings[0, 1] = 0.7
    assay2.readings[1, 0] = 0.3
    assay2.readings[1, 1] = 3.8

    assays = [assay1, assay2]

    # Test all_csv export
    output = io.StringIO()
    writer = csv.writer(output)
    Assay.all_csv(writer, assays)

    csv_content = output.getvalue().strip()
    lines = csv_content.split("\n")

    # We should have a header line plus 8 data lines (2 assays x 4 cells each)
    assert len(lines) == 9

    # Check header line
    header = lines[0]
    assert "id" in header
    assert "specimen" in header
    assert "machine" in header
    assert "person" in header
    assert "performed" in header

    # Check content for first assay
    first_assay_lines = [line for line in lines if "A0001" in line]
    assert len(first_assay_lines) == 4  # 4 cells in the assay

    # Check content for second assay
    second_assay_lines = [line for line in lines if "A0002" in line]
    assert len(second_assay_lines) == 4  # 4 cells in the assay

    # Verify some specific content is present
    assert any("S0001" in line for line in first_assay_lines)
    assert any("S0002" in line for line in second_assay_lines)
    assert any("M0001" in line for line in first_assay_lines)
    assert any("M0002" in line for line in second_assay_lines)
    assert any("2025-01-01" in line for line in first_assay_lines)
    assert any("2025-01-02" in line for line in second_assay_lines)
