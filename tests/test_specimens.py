"""Test specimen generation."""

import csv
from datetime import date
import io
import pytest
import random

from snailz import specimens_generate
from snailz.defaults import DEFAULT_SPECIMEN_PARAMS
from snailz.specimens import (
    BASES,
    Point,
    Specimen,
    AllSpecimens,
    SpecimenParams,
    _adjust_masses_by_location,
    _mutate_mass,
    _place_specimens_on_grid,
)
from snailz.grid import Grid, GridParams
from snailz.defaults import DEFAULT_GRID_PARAMS

from utils import check_params_stored


@pytest.mark.parametrize(
    "name, value",
    [
        ("length", 0),
        ("max_mass", 0.5 * DEFAULT_SPECIMEN_PARAMS.min_mass),
        ("min_mass", -1.0),
        ("mutations", DEFAULT_SPECIMEN_PARAMS.length * 2),
        ("number", 0),
        ("extra", 99),
        ("end_date", date(2025, 3, 1)),  # End date before start date
    ],
)
def test_specimens_fail_bad_parameter_value(name, value):
    """Test specimen generation fails with invalid parameter values."""
    params_dict = DEFAULT_SPECIMEN_PARAMS.model_dump()
    params_dict[name] = value
    with pytest.raises(ValueError):
        SpecimenParams(**params_dict)


@pytest.mark.parametrize("seed", [127893, 47129, 990124, 512741, 44109318])
def test_specimens_valid_result(seed):
    random.seed(seed)
    params = DEFAULT_SPECIMEN_PARAMS.model_copy(update={"seed": seed})
    result = specimens_generate(params)
    check_params_stored(params, result)

    assert len(result.reference) == result.params.length
    assert len(result.individuals) == result.params.number
    assert all(len(ind.genome) == result.params.length for ind in result.individuals)
    assert 0 <= result.susceptible_locus < result.params.length
    assert result.susceptible_base in BASES
    assert all(
        result.params.min_mass <= ind.mass <= result.params.max_mass
        for ind in result.individuals
    )

    # Check identifiers
    identifiers = [ind.ident for ind in result.individuals]
    assert all(len(ident) == 6 for ident in identifiers)
    assert all(ident[:2] == identifiers[0][:2] for ident in identifiers)
    assert identifiers[0][:2].isalpha() and identifiers[0][:2].isupper()
    assert len(set(identifiers)) == len(identifiers)
    for ident in identifiers:
        suffix = ident[2:]
        assert len(suffix) == 4
        assert all(c.isupper() or c.isdigit() for c in suffix)


@pytest.fixture
def output_specimens():
    """Create a small test specimen dataset."""
    individuals = [
        Specimen(
            genome="ACGT",
            ident="AB1234",
            mass=1.5,
            site=Point(x=1, y=2),
            collected_on=date(2025, 3, 10),
        ),
        Specimen(
            genome="TGCA",
            ident="AB5678",
            mass=1.8,
            site=Point(x=3, y=4),
            collected_on=date(2025, 3, 15),
        ),
    ]

    params = SpecimenParams(
        length=4,
        max_mass=10.0,
        min_mass=1.0,
        mut_scale=0.5,
        mutations=2,
        number=2,
        seed=12345,
        start_date=date(2025, 3, 5),
        end_date=date(2025, 3, 19),
    )

    return AllSpecimens(
        individuals=individuals,
        loci=[0, 1, 2],
        params=params,
        reference="ACGT",
        susceptible_base="A",
        susceptible_locus=0,
    )


def test_specimens_to_csv(output_specimens):
    """Test specimens to_csv method creates CSV representation."""
    csv_content = output_specimens.to_csv()
    rows = list(csv.reader(io.StringIO(csv_content)))

    assert len(rows) == 3  # Header + 2 specimens
    assert rows[0] == ["ident", "x", "y", "genome", "mass", "collected_on"]
    assert rows[1] == ["AB1234", "1", "2", "ACGT", "1.5", "2025-03-10"]
    assert rows[2] == ["AB5678", "3", "4", "TGCA", "1.8", "2025-03-15"]


def test_specimens_mass_adjusted_when_grid_provided():
    """Test that specimens have their masses adjusted when placed on a grid."""
    # Create a grid where all cells have a value to ensure mutation
    grid_params = GridParams(depth=8, seed=12345, size=11)
    all_cells_grid = Grid(
        grid=[[1 for x in range(11)] for y in range(11)],
        params=grid_params,
        start=Point(x=5, y=5),
    )

    # Create a specimen with known properties - susceptible genome
    specimen = Specimen(
        genome="ACGT",
        ident="TEST01",
        mass=10.0,  # Initial mass
        site=Point(x=None, y=None),
        collected_on=date(2025, 3, 10),
    )

    specimen_params = SpecimenParams(
        length=4,
        max_mass=20.0,
        min_mass=5.0,
        mut_scale=0.5,
        mutations=2,
        number=1,
        seed=12345,
        start_date=date(2025, 3, 5),
        end_date=date(2025, 3, 19),
    )

    specimens_obj = AllSpecimens(
        individuals=[specimen],
        loci=[0, 1],
        params=specimen_params,
        reference="ACGT",
        susceptible_base="A",  # First base is susceptible
        susceptible_locus=0,  # At position 0
    )

    # Control random number generation for predictable test
    random.seed(grid_params.seed)

    # Record the original mass
    original_mass = specimen.mass

    # Place specimen on grid and adjust mass
    _place_specimens_on_grid(all_cells_grid, specimens_obj)
    _adjust_masses_by_location(all_cells_grid, specimens_obj, 0.5)

    # Check coordinates were assigned
    assert specimen.site.x is not None
    assert specimen.site.y is not None

    # Check if mass was adjusted (every cell in grid has value 1)
    assert specimen.mass > original_mass, "Specimen mass should be adjusted"

    # Now test specimens_generate full workflow
    # Create params for specimen generation
    params = SpecimenParams(
        length=4,
        max_mass=20.0,
        min_mass=10.0,
        mut_scale=0.5,
        mutations=2,
        number=10,
        seed=12345,
        start_date=date(2025, 3, 5),
        end_date=date(2025, 3, 19),
    )

    # Force random numbers to be predictable
    random.seed(12345)

    # Generate specimens with the grid
    result = specimens_generate(params, all_cells_grid)

    # Verify all specimens have site coordinates
    for ind in result.individuals:
        assert ind.site.x is not None
        assert ind.site.y is not None
        assert 0 <= ind.site.x < len(all_cells_grid.grid), (
            "Site x should be within grid bounds"
        )
        assert 0 <= ind.site.y < len(all_cells_grid.grid), (
            "Site y should be within grid bounds"
        )

    # Verify masses are set initially based on susceptibility
    # and then adjusted based on location
    susceptible_specimens = []
    non_susceptible_specimens = []

    for ind in result.individuals:
        if ind.genome[result.susceptible_locus] == result.susceptible_base:
            susceptible_specimens.append(ind)
        else:
            non_susceptible_specimens.append(ind)

    # We should have at least susceptible specimens
    assert len(susceptible_specimens) > 0, (
        "Should have at least one susceptible specimen"
    )
    # With random generation, we might not get non-susceptible specimens in every test run

    # All susceptible specimens in polluted areas should have higher masses
    # All specimens in polluted areas get adjusted
    for ind in susceptible_specimens:
        x, y = ind.site.x, ind.site.y
        if all_cells_grid.grid[x][y] > 0:
            # For our test grid, all cells have value 1
            # With mut_scale=0.5, mass should be 1.5x the original
            midpoint = (params.max_mass + params.min_mass) / 2
            assert ind.mass >= midpoint * 1.5, (
                "Susceptible specimen mass should be adjusted upward"
            )


def test_specimens_initial_masses_based_on_susceptibility():
    """Test that specimens get initial masses based on susceptibility and not adjusted without grid."""
    random.seed(DEFAULT_SPECIMEN_PARAMS.seed)
    result = specimens_generate(DEFAULT_SPECIMEN_PARAMS)

    # Verify that site coordinates are empty without grid
    for ind in result.individuals:
        assert ind.site.x is None
        assert ind.site.y is None

    # Verify masses are within the original range
    for ind in result.individuals:
        assert (
            DEFAULT_SPECIMEN_PARAMS.min_mass
            <= ind.mass
            <= DEFAULT_SPECIMEN_PARAMS.max_mass
        )

    # Check that susceptible specimens have higher initial masses
    midpoint = (DEFAULT_SPECIMEN_PARAMS.max_mass + DEFAULT_SPECIMEN_PARAMS.min_mass) / 2

    susceptible_specimens = []
    non_susceptible_specimens = []

    for ind in result.individuals:
        if ind.genome[result.susceptible_locus] == result.susceptible_base:
            susceptible_specimens.append(ind)
        else:
            non_susceptible_specimens.append(ind)

    # With enough specimens, we should have both types
    if susceptible_specimens and non_susceptible_specimens:
        # Susceptible specimens should have higher masses
        for ind in susceptible_specimens:
            assert ind.mass >= midpoint, (
                "Susceptible specimens should have higher initial masses"
            )

        # Non-susceptible specimens should have lower masses
        for ind in non_susceptible_specimens:
            assert ind.mass <= midpoint, (
                "Non-susceptible specimens should have lower initial masses"
            )


@pytest.fixture
def mutation_specimens():
    """Default specimens for mutation tests (also initializes RNG)."""
    random.seed(DEFAULT_SPECIMEN_PARAMS.seed)
    return specimens_generate(DEFAULT_SPECIMEN_PARAMS)


def test_place_specimens_without_mass_adjustment(mutation_specimens):
    """Test that placing specimens on a grid with zero values doesn't change masses."""
    size = DEFAULT_GRID_PARAMS.size
    grid = Grid(
        grid=[[0 for _ in range(size)] for _ in range(size)],
        params=DEFAULT_GRID_PARAMS,
        start=Point(x=size // 2, y=size // 2),
    )
    original_masses = [ind.mass for ind in mutation_specimens.individuals]

    # Check that sites are initially None for x and y
    for ind in mutation_specimens.individuals:
        assert ind.site.x is None
        assert ind.site.y is None

    # Place specimens on grid
    _place_specimens_on_grid(grid, mutation_specimens)

    # Check that site coordinates have been updated
    for ind in mutation_specimens.individuals:
        assert ind.site.x is not None
        assert ind.site.y is not None
        assert 0 <= ind.site.x < size
        assert 0 <= ind.site.y < size

    # Adjust masses - but since all cells are zero, no changes should occur
    _adjust_masses_by_location(grid, mutation_specimens, 0.1)

    # Check masses haven't changed
    current_masses = [ind.mass for ind in mutation_specimens.individuals]
    assert current_masses == original_masses


def test_mass_adjustment_with_susceptible_genomes(mutation_specimens):
    """Test that mass adjustment occurs only with non-zero cells and susceptible genomes."""
    size = 11
    params = DEFAULT_GRID_PARAMS.model_copy(update={"size": size})
    grid = Grid(
        grid=[[1 for _ in range(size)] for _ in range(size)],
        params=params,
        start=Point(x=size // 2, y=size // 2),
    )

    # Make a copy of the original masses
    original_masses = [ind.mass for ind in mutation_specimens.individuals]

    # Make half the genomes susceptible and half not
    susc_locus = mutation_specimens.susceptible_locus
    susc_base = mutation_specimens.susceptible_base
    other_bases = [b for b in BASES if b != susc_base]
    for i, individual in enumerate(mutation_specimens.individuals):
        genome_list = list(individual.genome)
        if i % 2 == 0:
            genome_list[susc_locus] = susc_base
        else:
            genome_list[susc_locus] = random.choice(other_bases)
        individual.genome = "".join(genome_list)

    # Place specimens and then adjust masses
    _place_specimens_on_grid(grid, mutation_specimens)
    _adjust_masses_by_location(grid, mutation_specimens, mut_scale=3.0)

    # Verify sites are assigned correctly
    for individual in mutation_specimens.individuals:
        # All individuals should have site coordinates
        assert 0 <= individual.site.x < size
        assert 0 <= individual.site.y < size

    # For specimens with modified genomes where we control the susceptibility,
    # we can still test that the mass adjusts correctly
    for i, individual in enumerate(mutation_specimens.individuals):
        if i % 2 == 0 and individual.genome[susc_locus] == susc_base:
            # This specimen is susceptible and placed on a grid with value 1
            # Its mass should be adjusted by the mut_scale factor
            x, y = individual.site.x, individual.site.y
            if grid.grid[x][y] > 0:
                expected_mass = _mutate_mass(original_masses[i], 3.0, 1)
                assert individual.mass == pytest.approx(expected_mass)


def test_mass_adjustment_with_variable_grid_values():
    """Test that cell values affect mass adjustment magnitude."""
    # Create controlled specimens with predictable masses
    num_specimens = 5
    masses = [1.0, 2.0, 3.0, 4.0, 5.0]
    genomes = ["A" * 10 for _ in range(num_specimens)]
    susc_locus = 5
    susc_base = "A"
    identifiers = ["AB1234", "AB5678", "AB90CD", "ABEF12", "AB3456"]
    individuals = [
        Specimen(
            genome=g,
            mass=m,
            site=Point(x=0, y=0),
            ident=i,
            collected_on=date(2025, 3, 10),
        )
        for g, m, i in zip(genomes, masses.copy(), identifiers)
    ]

    specimen_params = SpecimenParams(
        length=10,
        max_mass=20.0,
        min_mass=1.0,
        mut_scale=0.5,
        mutations=3,
        number=num_specimens,
        seed=12345,
        start_date=date(2025, 3, 5),
        end_date=date(2025, 3, 19),
    )

    specimens = AllSpecimens(
        individuals=individuals,
        loci=[1, 2, 3],
        params=specimen_params,
        reference=("A" * 10),
        susceptible_base=susc_base,
        susceptible_locus=susc_locus,
    )

    # Test with different grid values
    mut_scale = 0.5
    for cell_value in range(num_specimens):
        specimen_index = cell_value
        test_grid = Grid(
            grid=[[cell_value]],
            params={"size": 1, "depth": 8, "seed": 123},
            start=Point(x=0, y=0),
        )

        # Reset mass to original value for this test case
        specimens.individuals[specimen_index].mass = masses[specimen_index]
        original_mass = specimens.individuals[specimen_index].mass

        # Place specimen at 0,0 and adjust mass
        specimens.individuals[specimen_index].site.x = 0
        specimens.individuals[specimen_index].site.y = 0

        # Adjust mass based on location
        _adjust_masses_by_location(
            test_grid, specimens, mut_scale, specific_index=specimen_index
        )

        # Check mass result
        if cell_value > 0:
            expected_mass = _mutate_mass(original_mass, mut_scale, cell_value)
            assert specimens.individuals[specimen_index].mass == pytest.approx(
                expected_mass
            )
        else:
            assert specimens.individuals[specimen_index].mass == original_mass
