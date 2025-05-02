"""Test effects functionality."""

from datetime import date
import random
import pytest

from snailz.assays import Assay
from snailz.effects import apply_effects, assign_sample_locations, choose_assay_date
from snailz.grid import Grid
from snailz.machines import Machine
from snailz.params import AssayParams, ScenarioParams, SpecimenParams
from snailz.persons import Person
from snailz.scenario import Scenario
from snailz.specimens import Specimen, AllSpecimens


def test_assign_sample_locations():
    random.seed(42)
    grid1 = Grid(id="G01", size=3)
    grid2 = Grid(id="G02", size=3)

    # Create test specimens
    params = SpecimenParams()
    specimens = AllSpecimens.generate(params, 5)

    # Before assignment, all specimens should have default location
    for s in specimens.samples:
        assert s.grid == ""
        assert s.x == -1
        assert s.y == -1

    # Assign locations
    assign_sample_locations([grid1, grid2], specimens)

    # After assignment, all specimens should have valid locations
    for s in specimens.samples:
        assert s.grid in ["G01", "G02"]
        assert 0 <= s.x < 3
        assert 0 <= s.y < 3

    # Check that assignments are unique
    locations = [(s.grid, s.x, s.y) for s in specimens.samples]
    assert len(locations) == len(set(locations))


def test_choose_assay_date():
    random.seed(42)
    params = AssayParams(max_delay=7)
    sample_date = date(2025, 1, 1)

    specimen = Specimen(
        id="S0001", genome="ACGT", is_mutant=False, mass=10.0, sampled=sample_date
    )

    # Test that the assay date is after the sampling date
    for _ in range(10):
        assay_date = choose_assay_date(params, specimen)
        assert assay_date > specimen.sampled

        # Test that the assay date is within the max delay
        days_diff = (assay_date - specimen.sampled).days
        assert 1 <= days_diff <= params.max_delay


def test_apply_effects():
    random.seed(42)
    params = ScenarioParams(
        rng_seed=42,
        specimen_params=SpecimenParams(mut_mass_scale=2.0),
        assay_params=AssayParams(),
        pollution_scale=0.1,
        delay_scale=0.05,
    )

    # Create grid with pollution levels
    grid = Grid(id="G01", size=3)
    for x in range(3):
        for y in range(3):
            grid[x, y] = x + y  # Simple pollution gradient

    # Create specimens
    normal_specimen = Specimen(
        id="S0001",
        genome="ACGT",
        is_mutant=False,
        mass=10.0,
        grid="G01",
        x=0,
        y=0,
        sampled=date(2025, 1, 1),
    )
    mutant_specimen = Specimen(
        id="S0002",
        genome="ACGT",
        is_mutant=True,
        mass=10.0,
        grid="G01",
        x=2,
        y=2,
        sampled=date(2025, 1, 1),
    )

    # Create AllSpecimens object
    specimens = AllSpecimens(
        params=SpecimenParams(),
        ref_genome="ACGT",
        susc_locus=0,
        susc_base="T",
        samples=[normal_specimen, mutant_specimen],
    )

    # Create assay treatments and readings
    treatments = Grid(size=2)
    readings = Grid(size=2)
    treatments[0, 0] = "C"
    treatments[0, 1] = "S"
    treatments[1, 0] = "S"
    treatments[1, 1] = "C"
    readings[0, 0] = 1.0  # Control
    readings[0, 1] = 5.0  # Specimen
    readings[1, 0] = 5.0  # Specimen
    readings[1, 1] = 1.0  # Control

    # Create an assay with a delay of 5 days
    assay = Assay(
        id="A0001",
        specimen_id="S0002",  # Using the mutant specimen
        machine_id="M0001",
        person_id="P0001",
        performed=date(2025, 1, 6),  # 5 days after sampling
        treatments=treatments,
        readings=readings,
    )

    # Create a machine and person
    machine = Machine(id="M0001", name="Test Machine")
    person = Person(id="P0001", family="Doe", personal="Jane")

    # Create scenario
    scenario = Scenario(
        params=params,
        grids=[grid],
        specimens=specimens,
        machines=[machine],
        persons=[person],
        assays=[assay],
        images={},  # Empty images dictionary
    )

    # Record initial values
    initial_normal_mass = normal_specimen.mass
    initial_mutant_mass = mutant_specimen.mass

    # Record initial reading values
    initial_readings = {}
    for x in range(assay.readings.size):
        for y in range(assay.readings.size):
            initial_readings[(x, y)] = assay.readings[x, y]

    # Apply effects
    apply_effects(scenario)

    # Test 1: Normal specimen mass should remain unchanged
    assert normal_specimen.mass == initial_normal_mass

    # Test 2: Mutant specimen mass should increase due to mutation and pollution
    # Mutation effect multiplies by mut_mass_scale (2.0)
    # Pollution effect adds mass * pollution_scale * pollution_level
    # At position (2, 2), pollution level is 4
    expected_mass = initial_mutant_mass * 2.0  # Mutation effect
    expected_mass += expected_mass * 0.1 * 4  # Pollution effect
    assert mutant_specimen.mass == pytest.approx(expected_mass)

    # Test 3: Control readings (C) should remain unchanged
    assert assay.readings[0, 0] == initial_readings[(0, 0)]
    assert assay.readings[1, 1] == initial_readings[(1, 1)]

    # Test 4: Specimen readings (S) should decrease due to delay
    # Delay is 5 days, and delay_scale is 0.05
    expected_drop_factor = 5 * 0.05  # 25% drop
    for x, y in [(0, 1), (1, 0)]:
        if assay.treatments[x, y] == "S":
            expected_reading = initial_readings[(x, y)] * (1 - expected_drop_factor)
            assert assay.readings[x, y] == pytest.approx(expected_reading)
