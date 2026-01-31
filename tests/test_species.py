"""Test species construction."""

import csv
from dataclasses import fields
from pathlib import Path
import pytest
from sqlite_utils import Database
from snailz import Parameters, Species
from snailz.species import BASES


@pytest.fixture
def a_species():
    return Species.make(Parameters(genome_length=20, num_loci=5))[0]


def test_species_reference_genome_length_and_bases(seeded_rng):
    genome = Species._reference_genome(Parameters(genome_length=50))
    assert len(genome) == 50
    assert set(genome).issubset(set(BASES.keys()))


def test_species_make_constructs_consistent_species(a_species):
    assert len(a_species.reference) == 20
    assert len(a_species.loci) == 5
    assert a_species.susc_locus in a_species.loci
    assert a_species.susc_base != a_species.reference[a_species.susc_locus]


def test_species_random_genome_no_mutation_matches_reference(seeded_rng):
    params = Parameters(genome_length=30, num_loci=10, p_mutation=0.0)
    species = Species.make(params)[0]
    genome = species.random_genome(params)
    assert genome == species.reference


def test_species_random_genome_full_mutation_changes_only_loci(seeded_rng):
    params = Parameters(genome_length=40, num_loci=8, p_mutation=1.0)
    species = Species.make(params)[0]
    genome = species.random_genome(params)
    for i, (ref_base, new_base) in enumerate(zip(species.reference, genome)):
        if i in species.loci:
            assert new_base in BASES[ref_base]
        else:
            assert new_base == ref_base


def test_species_persist_to_csv(tmp_path):
    params = Parameters(genome_length=40, num_loci=8, p_mutation=1.0)
    species = Species.make(params)
    Species.save_csv(tmp_path, species)

    with open(Path(tmp_path, f"{Species.table_name}.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 2

    with open(Path(tmp_path, "species_loci.csv"), "r") as reader:
        rows = list(csv.reader(reader))
        assert len(rows) == 9


def test_grid_persist_to_db(a_species):
    db = Database(memory=True)
    Species.save_db(db, [a_species])

    rows = list(db[Species.table_name].rows)
    assert len(rows) == 1
    field_names = {f.name for f in fields(a_species)}
    assert set(rows[0].keys()).issubset(field_names)

    rows = list(db["species_loci"].rows)
    assert len(rows) == len(a_species.loci)
    loci = {r["locus"] for r in rows}
    assert all(loc in loci for loc in a_species.loci)
