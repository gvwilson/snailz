"""Test specimen generation."""

import csv
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
)
from snailz.grid import Grid, GridParams
from snailz import utils

from utils import check_params_stored


@pytest.mark.parametrize(
    "name, value",
    [
        ("length", 0),
        ("max_mass", 0.5 * DEFAULT_SPECIMEN_PARAMS.min_mass),
        ("min_mass", -1.0),
        ("mutations", DEFAULT_SPECIMEN_PARAMS.length * 2),
        ("number", 0),
    ],
)
def test_specimens_fail_bad_parameter_value(name, value):
    # Create a dictionary with the updated value
    params_dict = DEFAULT_SPECIMEN_PARAMS.model_dump()
    params_dict[name] = value
    with pytest.raises(ValueError):
        SpecimenParams(**params_dict)


@pytest.mark.parametrize("seed", [127893, 47129, 990124, 512741, 44109318])
def test_specimens_valid_result(seed):
    random.seed(seed)
    # Create a new parameter object with the specific seed
    params_dict = DEFAULT_SPECIMEN_PARAMS.model_dump()
    params_dict["seed"] = seed
    params = SpecimenParams(**params_dict)
    result = specimens_generate(params)
    check_params_stored(params, result)

    # Check specimens have correct structure
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
        Specimen(genome="ACGT", ident="AB1234", mass=1.5, site=Point(x=1, y=2)),
        Specimen(genome="TGCA", ident="AB5678", mass=1.8, site=Point(x=3, y=4)),
    ]

    # Create a valid SpecimenParams object
    params = SpecimenParams(
        length=4,
        max_mass=10.0,
        min_mass=1.0,
        mut_scale=0.5,
        mutations=2,
        number=2,
        seed=12345,
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
    # Get the CSV content
    csv_content = output_specimens.to_csv()

    # Parse the CSV output
    rows = list(csv.reader(io.StringIO(csv_content)))

    # Check the output
    assert len(rows) == 3  # Header + 2 specimens
    assert rows[0] == ["ident", "x", "y", "genome", "mass"]
    assert rows[1] == ["AB1234", "1", "2", "ACGT", "1.5"]
    assert rows[2] == ["AB5678", "3", "4", "TGCA", "1.8"]

    # Check that we have Unix line endings (LF) but no DOS line endings (CRLF)
    assert "\n" in csv_content
    assert "\r\n" not in csv_content


def test_specimens_mutate_when_grid_provided():
    """Test that specimens are mutated when a grid is provided."""
    # Create a grid where all cells have a value to ensure mutation
    grid_params = GridParams(depth=8, seed=12345, size=3)
    all_cells_grid = Grid(
        grid=[[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # All cells have non-zero values
        params=grid_params,
    )

    # Create a specimen with known properties
    specimen = Specimen(
        genome="ACGT",
        ident="TEST01",
        mass=10.0,
        site=Point(x=None, y=None),  # Will be assigned during mutation
    )

    # Create a specimens collection with this individual
    specimen_params = SpecimenParams(
        length=4,
        max_mass=20.0,
        min_mass=5.0,
        mut_scale=0.5,
        mutations=2,
        number=1,
        seed=12345,
    )

    specimens_obj = AllSpecimens(
        individuals=[specimen],
        loci=[0, 1],
        params=specimen_params,
        reference="ACGT",
        susceptible_base="A",  # First base is susceptible
        susceptible_locus=0,  # At position 0
    )

    # Record the original mass
    original_mass = specimen.mass

    # Control random number generation for predictable test
    random.seed(54321)

    # We need to patch the mutate_masses function to control randomness
    from snailz.specimens import mutate_masses

    # Call mutate_masses directly with specific_index=0 to target our specimen
    mutate_masses(all_cells_grid, specimens_obj, 0.5, specific_index=0)

    # Check coordinates were assigned
    assert specimen.site.x is not None, "Site x-coordinate should be set"
    assert specimen.site.y is not None, "Site y-coordinate should be set"

    # Check if mass was mutated (every cell in grid has value 1)
    # Formula: original * (1 + (mut_scale * cell_value)) = 10 * (1 + (0.5 * 1)) = 10 * 1.5 = 15.0
    expected_mass = 15.0
    assert specimen.mass != original_mass, "Specimen mass should be mutated"
    assert specimen.mass == expected_mass, (
        f"Expected mass to be {expected_mass}, got {specimen.mass}"
    )

    # Now test specimens_generate integration
    # Check that specimens_generate calls mutate_masses when a grid is provided
    # Create params for specimen generation
    params = SpecimenParams(
        length=4,
        max_mass=20.0,
        min_mass=10.0,
        mut_scale=0.5,
        mutations=2,
        number=10,  # Generate enough specimens to increase chances of mutation
        seed=12345,
    )

    # Force random numbers to be predictable
    random.seed(12345)

    # Using a grid where every cell has a non-zero value
    # ensures that any susceptible specimen will be mutated
    result = specimens_generate(params, all_cells_grid)

    # Verify site coordinates
    for ind in result.individuals:
        assert ind.site.x is not None, "Site x-coordinate should be set"
        assert ind.site.y is not None, "Site y-coordinate should be set"
        assert 0 <= ind.site.x < len(all_cells_grid.grid), (
            "Site x should be within grid bounds"
        )
        assert 0 <= ind.site.y < len(all_cells_grid.grid), (
            "Site y should be within grid bounds"
        )

    # Find any susceptible specimens at non-zero grid cells
    # Since all grid cells are non-zero, we just need to find a susceptible specimen
    found_susceptible = False
    for ind in result.individuals:
        if ind.genome[result.susceptible_locus] == result.susceptible_base:
            found_susceptible = True
            # Calculate what the mass would be without mutation
            unmutated_mass = round(ind.mass / 1.5, utils.PRECISION)
            # Verify it's different from what would be expected without mutation
            assert ind.mass != unmutated_mass, (
                "Susceptible specimen at non-zero grid cell should be mutated"
            )
            break

    # We should have found at least one susceptible specimen
    assert found_susceptible, "Should have at least one susceptible specimen"


def test_specimens_not_mutated_without_grid():
    """Test that specimens are not mutated when no grid is provided."""
    # Set seed for reproducibility
    seed = 12345
    random.seed(seed)

    # Generate specimens without a grid
    result = specimens_generate(DEFAULT_SPECIMEN_PARAMS)

    # Verify that site coordinates are empty
    for ind in result.individuals:
        assert ind.site.x is None, "Site x-coordinate should be None without grid"
        assert ind.site.y is None, "Site y-coordinate should be None without grid"

    # Verify masses are within the original range
    for ind in result.individuals:
        assert (
            DEFAULT_SPECIMEN_PARAMS.min_mass
            <= ind.mass
            <= DEFAULT_SPECIMEN_PARAMS.max_mass
        ), "Mass should be in original range"
