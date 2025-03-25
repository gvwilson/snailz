"""Generate snail specimens."""

import csv
import io
import random
import string

from pydantic import BaseModel, Field, model_validator

from . import utils
from .grid import Grid

# Bases.
BASES = "ACGT"


class SpecimenParams(BaseModel):
    """Parameters for specimen generation.

    - length: Length of specimen genomes (must be positive)
    - max_mass: Maximum mass for specimens (must be positive)
    - min_mass: Minimum mass for specimens (must be positive and less than max_mass)
    - mut_scale: Scale factor for mutation effect
    - mutations: Number of mutations in specimens (must be between 0 and length)
    - number: Number of specimens to generate (must be positive)
    - seed: Random seed for reproducibility
    """

    length: int = Field(gt=0)
    max_mass: float = Field(gt=0)
    min_mass: float = Field(gt=0)
    mut_scale: float = Field()
    mutations: int = Field(ge=0)
    number: int = Field(gt=0)
    seed: int = Field()

    @model_validator(mode="after")
    def validate_mass_range(self):
        """Validate that max_mass is greater than min_mass."""
        if self.min_mass >= self.max_mass:
            raise ValueError("max_mass must be greater than min_mass")
        return self

    @model_validator(mode="after")
    def validate_mutations_range(self):
        """Validate that mutations is not greater than genome length."""
        if self.mutations > self.length:
            raise ValueError("mutations must be between 0 and length")
        return self

    model_config = {"extra": "forbid"}


class Point(BaseModel):
    """A 2D point with x and y coordinates.

    - x: X coordinate in grid
    - y: Y coordinate in grid
    """

    x: int | None = None
    y: int | None = None


class Specimen(BaseModel):
    """A single specimen with unique identifier, genome, mass, and site location.

    - genome: bases in genome
    - ident: unique identifier
    - mass: snail mass in grams
    - site: grid location where specimen was collected
    """

    genome: str
    ident: str
    mass: float
    site: Point


class AllSpecimens(BaseModel):
    """A set of generated specimens.

    - individuals: list of individual specimens
    - loci: locations where mutations can occur
    - params: parameters used to generate this data
    - reference: unmutated genome
    - susceptible_base: mutant base that induces mass changes
    - susceptible_locus: location of mass change mutation
    """

    individuals: list[Specimen]
    loci: list[int]
    params: SpecimenParams
    reference: str
    susceptible_base: str
    susceptible_locus: int

    def to_csv(self) -> str:
        """Return a CSV string representation of the specimens data.

        Returns:
            A CSV-formatted string containing specimen data with fields:
            - ident: specimen identifier
            - x: X coordinate in grid
            - y: Y coordinate in grid
            - genome: bases in genome
            - mass: snail mass in grams
        """
        output = io.StringIO()
        writer = csv.writer(output, **utils.CSV_SETTINGS)
        writer.writerow(["ident", "x", "y", "genome", "mass"])
        for indiv in self.individuals:
            writer.writerow(
                [indiv.ident, indiv.site.x, indiv.site.y, indiv.genome, indiv.mass]
            )
        return output.getvalue()


def specimens_generate(params: SpecimenParams, grid: Grid = None) -> AllSpecimens:
    """Generate specimens with random genomes and masses.

    Each genome is a string of bases of the same length. One locus is
    randomly chosen as "significant", and a specific mutation there
    predisposes the snail to mass changes. Other mutations are added
    randomly at other loci.  Specimen masses are only mutated if a
    grid is provided.

    Parameters:
        params: SpecimenParams object
        grid: Grid object to place specimens on for mass mutation

    Returns:
        AllSpecimens object containing the generated specimens and parameters

    """
    loci = _make_loci(params)
    reference = _make_reference_genome(params)
    susc_loc = _choose_one(loci)
    susc_base = reference[susc_loc]
    genomes = [_make_genome(reference, loci) for i in range(params.number)]
    masses = _make_masses(params, genomes, susc_loc, susc_base)
    identifiers = _make_idents(params.number)

    individuals = [
        Specimen(genome=g, mass=m, site=Point(), ident=i)
        for g, m, i in zip(genomes, masses, identifiers)
    ]

    result = AllSpecimens(
        individuals=individuals,
        loci=loci,
        params=params,
        reference=reference,
        susceptible_base=susc_base,
        susceptible_locus=susc_loc,
    )

    if grid is not None:
        mutate_masses(grid, result, params.mut_scale)

    return result


def mutate_masses(
    grid: Grid,
    specimens: AllSpecimens,
    mut_scale: float,
    specific_index: int | None = None,
) -> None:
    """Mutate mass based on grid values and genetic susceptibility.

    For each specimen, choose a random cell from the grid and modify
    the mass if the cell's value is non-zero and the genome is
    susceptible. Records the chosen site coordinates for each specimen
    regardless of whether mutation occurs.  Modifies specimen masses
    in-place for susceptible individuals; updates site coordinates for
    all individuals.

    Parameters:
        grid: A Grid object containing pollution values
        specimens: A AllSpecimens object with individuals to potentially mutate
        mut_scale: Scaling factor for mutation effect
        specific_index: Optional index to mutate only a specific specimen
    """
    grid_size = len(grid.grid)
    susc_locus = specimens.susceptible_locus
    susc_base = specimens.susceptible_base

    if specific_index is None:
        individuals = specimens.individuals
    else:
        individuals = [specimens.individuals[specific_index]]

    for i in individuals:
        x = random.randrange(grid_size)
        y = random.randrange(grid_size)
        i.site.x = x
        i.site.y = y
        if grid.grid[x][y] > 0 and i.genome[susc_locus] == susc_base:
            i.mass = mutate_mass(i.mass, mut_scale, grid.grid[x][y])


def mutate_mass(original: float, mut_scale: float, cell_value: int) -> float:
    """Mutate a single specimen's mass.

    Parameters:
        original: The original mass value
        mut_scale: Scaling factor for mutation effect
        cell_value: The grid cell value affecting the mutation

    Returns:
        The mutated mass value, rounded to PRECISION decimal places
    """
    return round(original * (1 + (mut_scale * cell_value)), utils.PRECISION)


def _choose_one(values: list[int]) -> int:
    """Choose a single random item from a collection.

    Parameters:
        values: A sequence to choose from

    Returns:
        A randomly selected item from the values sequence
    """
    return random.choices(values, k=1)[0]


def _choose_other(values: str, exclude: str) -> str:
    """Choose a value at random except for the excluded values.

    Parameters:
        values: A collection to choose from
        exclude: Value or collection of values to exclude from the choice

    Returns:
        A randomly selected item from values that isn't in exclude
    """
    candidates = list(sorted(set(values) - set(exclude)))
    return candidates[random.randrange(len(candidates))]


def _make_genome(reference: str, loci: list[int]) -> str:
    """Make an individual genome by mutating the reference genome.

    Parameters:
        reference: Reference genome string to base the new genome on
        loci: List of positions that can be mutated

    Returns:
        A new genome string with random mutations at some loci
    """
    result = list(reference)
    num_mutations = random.randint(1, len(loci))
    for loc in random.sample(range(len(loci)), num_mutations):
        result[loc] = _choose_other(BASES, reference[loc])
    return "".join(result)


def _make_idents(count: int) -> list[str]:
    """Create unique specimen identifiers.

    Each identifier is a 6-character string:
    - First two characters are the same uppercase letters for all specimens
    - Remaining four chararacters are random uppercase letters and digits

    Parameters:
        count: Number of identifiers to generate

    Returns:
        List of unique specimen identifiers
    """
    prefix = "".join(random.choices(string.ascii_uppercase, k=2))
    chars = string.ascii_uppercase + string.digits
    gen = utils.UniqueIdGenerator(
        "specimens", lambda: f"{prefix}{''.join(random.choices(chars, k=4))}"
    )
    return [gen.next() for _ in range(count)]


def _make_loci(params: SpecimenParams) -> list[int]:
    """Make a list of mutable loci positions.

    Parameters:
        params: SpecimenParams with length and mutations attributes

    Returns:
        A list of unique randomly selected positions that can be mutated
    """
    return random.sample(list(range(params.length)), params.mutations)


def _make_masses(
    params: SpecimenParams,
    genomes: list[str],
    susceptible_locus: int,
    susceptible_base: str,
) -> list[float]:
    """Generate random masses for specimens.

    Parameters:
        params: SpecimenParams with min_mass and max_mass attributes
        genomes: List of genome strings
        susceptible_locus: Position that determines susceptibility
        susceptible_base: Base that makes a specimen susceptible

    Returns:
        List of randomly generated mass values between min_mass and max_mass,
        rounded to PRECISION decimal places
    """
    return [
        round(random.uniform(params.min_mass, params.max_mass), utils.PRECISION)
        for _ in genomes
    ]


def _make_reference_genome(params: SpecimenParams) -> str:
    """Make a random reference genome.

    Parameters:
        params: SpecimenParams with length attribute

    Returns:
        A randomly generated genome string of the specified length
    """
    return "".join(random.choices(BASES, k=params.length))
