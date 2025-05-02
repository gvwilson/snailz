"""Test specimen functionality."""

import csv
from datetime import date
import random

import pytest

from snailz.params import SpecimenParams
from snailz.specimens import Specimen, AllSpecimens, BASES


def test_generate_invalid_number_of_specimens():
    random.seed(42)
    params = SpecimenParams()
    with pytest.raises(ValueError):
        AllSpecimens.generate(params, 0)


def test_specimen_generation():
    random.seed(42)
    params = SpecimenParams()
    ref_genome = "ACGT"
    susc_locus = 2
    susc_base = "T"

    # Generate a non-mutant specimen
    specimen = Specimen.generate(params, ref_genome, False, susc_locus, susc_base)

    assert specimen.id.startswith("S")
    assert len(specimen.genome) == len(ref_genome)
    assert specimen.is_mutant is False
    assert specimen.mass > 0
    assert isinstance(specimen.sampled, date)

    # Generate a mutant specimen
    mutant = Specimen.generate(params, ref_genome, True, susc_locus, susc_base)

    assert mutant.is_mutant is True
    assert mutant.genome[susc_locus] == susc_base


def test_all_specimens_generation():
    random.seed(42)
    params = SpecimenParams()
    num_specimens = 10

    specimens = AllSpecimens.generate(params, num_specimens)

    assert len(specimens.samples) == num_specimens
    assert len(specimens.ref_genome) == params.genome_length
    assert 0 <= specimens.susc_locus < params.genome_length
    assert specimens.susc_base in BASES

    # Check that we have some mutants
    mutants = [s for s in specimens.samples if s.is_mutant]
    assert len(mutants) > 0

    # Check that mutants have the susceptible base at the susceptible locus
    for mutant in mutants:
        assert mutant.genome[specimens.susc_locus] == specimens.susc_base


def test_specimen_csv_export(tmp_path):
    random.seed(42)
    params = SpecimenParams()
    specimens = AllSpecimens.generate(params, 5)

    # Assign grid locations for testing
    for i, specimen in enumerate(specimens.samples):
        specimen.grid = f"G{i + 1:02d}"
        specimen.x = i
        specimen.y = i

    csv_path = tmp_path / "specimens.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        specimens.to_csv(writer)

    with open(csv_path, "r") as f:
        lines = f.readlines()
    assert len(lines) == 6  # header + 5 specimens
    assert "id,genome,mass,grid,x,y,sampled" in lines[0]

    # Check each specimen is in the file
    for specimen in specimens.samples:
        found = False
        for line in lines[1:]:
            if specimen.id in line and specimen.grid in line:
                found = True
                break
        assert found
