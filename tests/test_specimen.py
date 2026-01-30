"""Test specimen construction."""

from datetime import date
import pytest

from snailz import Grid, Parameters, Specimen


@pytest.fixture
def a_grid(seeded_rng):
    return Grid(size=5, spacing=1.0, lat0=0.0, lon0=0.0, params=Parameters())


class DummySpecies:
    def __init__(self, genome):
        self.genome = genome

    def random_genome(self, params):
        return self.genome


def test_specimen_post_init_assigns_id_and_validates(seeded_rng):
    specimen = Specimen(
        lat=10.0,
        lon=20.0,
        genome="ACGT",
        mass=1.0,
        diameter=1.0,
        collected=date(2026, 1, 1),
    )
    assert specimen.ident.startswith("S")
    assert len(specimen.genome) > 0
    assert specimen.lat == 10.0
    assert specimen.lon == 20.0
    assert specimen.mass == 1.0
    assert specimen.diameter == 1.0


def test_specimen_post_init_rejects_empty_genome(seeded_rng):
    with pytest.raises(ValueError):
        Specimen(lat=0.0, lon=0.0, genome="", mass=1.0)


def test_specimen_make_creates_correct_number_of_specimens(a_grid):
    grids = [a_grid]
    fixed_genome = "AACCGGTT"
    species = DummySpecies(genome=fixed_genome)
    specimens = Specimen.make(
        Parameters(num_specimens=3, p_mutation=0.5), grids, species
    )
    assert len(specimens) == 3
    assert all(isinstance(s, Specimen) for s in specimens)
    assert all(s.genome == fixed_genome for s in specimens)


def test_specimen_make_coordinates_within_grid(a_grid):
    grids = [a_grid]
    species = DummySpecies(genome="ACGT")
    specimens = Specimen.make(
        Parameters(num_specimens=20, p_mutation=0.2), grids, species
    )
    assert all(0.0 <= s.lat < 10.0 for s in specimens)
    assert all(0.0 <= s.lon < 10.0 for s in specimens)
