"""Test mass mutation functionality."""

import pytest
import random
from unittest.mock import patch

from snailz.defaults import DEFAULT_SPECIMEN_PARAMS
from snailz.grid import Grid, GridParams
from snailz import specimens_generate
from snailz.specimens import (
    BASES,
    SpecimenParams,
    AllSpecimens,
    Specimen,
    Point,
    mutate_masses,
    mutate_mass,
)


def test_mutate_mass_no_effect_on_zero_cells():
    """Test that zero cells in grid don't affect mass but site coordinates are updated."""
    random.seed(DEFAULT_SPECIMEN_PARAMS.seed)
    specimens = specimens_generate(DEFAULT_SPECIMEN_PARAMS)
    grid_params = GridParams(size=5, depth=8, seed=123)
    grid = Grid(
        grid=[[0 for _ in range(5)] for _ in range(5)],
        params=grid_params,
    )
    original_masses = [ind.mass for ind in specimens.individuals]

    # Check that sites are initially None for x and y
    for ind in specimens.individuals:
        assert ind.site.x is None
        assert ind.site.y is None

    mutate_masses(grid, specimens, 0.1)

    # Check masses haven't changed
    current_masses = [ind.mass for ind in specimens.individuals]
    assert current_masses == original_masses

    # Check that site coordinates have been updated
    for ind in specimens.individuals:
        assert ind.site.x is not None
        assert ind.site.y is not None
        assert 0 <= ind.site.x < 5
        assert 0 <= ind.site.y < 5


def test_mutate_mass_effect_with_susceptible_genomes():
    """Test that mutations occur only with non-zero cells and susceptible genomes."""
    random.seed(DEFAULT_SPECIMEN_PARAMS.seed)
    specimens = specimens_generate(DEFAULT_SPECIMEN_PARAMS)

    # Create a grid with all cells = 1
    grid_params = GridParams(size=5, depth=8, seed=123)
    grid = Grid(
        grid=[[1 for _ in range(5)] for _ in range(5)],
        params=grid_params,
    )

    # Make a copy of the original masses
    original_masses = [ind.mass for ind in specimens.individuals]

    # Make half the genomes susceptible and half not
    susc_locus = specimens.susceptible_locus
    susc_base = specimens.susceptible_base
    other_bases = [b for b in BASES if b != susc_base]
    for i, individual in enumerate(specimens.individuals):
        genome_list = list(individual.genome)
        if i % 2 == 0:
            genome_list[susc_locus] = susc_base
        else:
            genome_list[susc_locus] = random.choice(other_bases)
        individual.genome = "".join(genome_list)

    # Mutate
    mut_scale = 3.0
    mutate_masses(grid, specimens, mut_scale)

    # Verify only susceptible genomes have changed but all sites are recorded
    for i, individual in enumerate(specimens.individuals):
        # All individuals should have site coordinates
        assert individual.site.x is not None
        assert individual.site.y is not None
        assert 0 <= individual.site.x < 5
        assert 0 <= individual.site.y < 5

        # Only susceptible individuals should have changed mass
        if i % 2 == 0:
            expected_mass = mutate_mass(original_masses[i], mut_scale, 1)
            assert individual.mass == pytest.approx(expected_mass)
        else:
            assert individual.mass == original_masses[i]


def test_mutate_mass_with_variable_grid_values():
    """Test that cell values affect mutation magnitude and site coordinates are recorded."""
    # Create controlled specimens with predictable masses
    num_specimens = 5
    masses = [1.0, 2.0, 3.0, 4.0, 5.0]
    genomes = ["A" * 10 for _ in range(num_specimens)]
    susc_locus = 5
    susc_base = "A"

    identifiers = ["AB1234", "AB5678", "AB90CD", "ABEF12", "AB3456"]

    individuals = [
        Specimen(genome=g, mass=m, site=Point(), ident=i)
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
            grid=[[cell_value]], params={"size": 1, "depth": 8, "seed": 123}
        )
        original_mass = specimens.individuals[specimen_index].mass

        with patch("random.randrange", return_value=0):
            mutate_masses(
                test_grid, specimens, mut_scale, specific_index=specimen_index
            )

        # Check site is recorded
        assert specimens.individuals[specimen_index].site.x == 0
        assert specimens.individuals[specimen_index].site.y == 0

        # Check mass result
        if cell_value > 0:
            expected_mass = mutate_mass(original_mass, mut_scale, cell_value)
            assert specimens.individuals[specimen_index].mass == pytest.approx(
                expected_mass
            )
        else:
            assert specimens.individuals[specimen_index].mass == original_mass
