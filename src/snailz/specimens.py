"""Generate snail specimens.

This module handles the generation of snail specimens with the following process:
1. Generate genomes with random mutations
2. Assign initial masses based on whether they have the significant mutation
3. Place specimens randomly on the grid (no two snails in the same cell)
4. Adjust masses based on whether their location is polluted or not
"""

import io
import random
import string
from datetime import date

from pydantic import BaseModel, Field, model_validator

from . import utils
from .grid import Grid
from .utils import Point

# Bases.
BASES = "ACGT"


class SpecimenParams(BaseModel):
    """Parameters for specimen generation."""

    end_date: date = Field(description="End date for specimen collection")
    length: int = Field(
        gt=0, description="Length of specimen genomes (must be positive)"
    )
    max_mass: float = Field(
        gt=0, description="Maximum mass for specimens (must be positive)"
    )
    min_mass: float = Field(
        gt=0,
        description="Minimum mass for specimens (must be positive and less than max_mass)",
    )
    mut_scale: float = Field(ge=0, description="Scale factor for mutation effect")
    mutations: int = Field(
        ge=0,
        description="Number of mutations in specimens (must be between 0 and length)",
    )
    number: int = Field(
        gt=0, description="Number of specimens to generate (must be positive)"
    )
    seed: int = Field(ge=0, description="Random seed for reproducibility")
    start_date: date = Field(description="Start date for specimen collection")

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_fields(self):
        """Validate requirements on fields."""
        if self.min_mass >= self.max_mass:
            raise ValueError("max_mass must be greater than min_mass")
        if self.mutations > self.length:
            raise ValueError("mutations must be between 0 and length")
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class Specimen(BaseModel):
    """A single specimen."""

    ident: str = Field(description="unique identifier")
    collected_on: date = Field(description="date when specimen was collected")
    genome: str = Field(description="bases in genome")
    mass: float = Field(gt=0, description="snail mass in grams")
    site: Point = Field(description="grid location where specimen was collected")


class AllSpecimens(BaseModel):
    """A set of generated specimens."""

    individuals: list[Specimen] = Field(description="list of individual specimens")
    loci: list[int] = Field(description="locations where mutations can occur")
    params: SpecimenParams = Field(description="parameters used to generate this data")
    reference: str = Field(description="unmutated genome")
    susceptible_base: str = Field(description="mutant base that induces mass changes")
    susceptible_locus: int = Field(ge=0, description="location of mass change mutation")

    def to_csv(self) -> str:
        """Return a CSV string representation of the specimens data.

        Returns:
            A CSV-formatted string with people data (without parameters)
        """

        output = io.StringIO()
        writer = utils.csv_writer(output)
        writer.writerow(["ident", "x", "y", "genome", "mass", "collected_on"])
        for indiv in self.individuals:
            writer.writerow(
                [
                    indiv.ident,
                    indiv.site.x,
                    indiv.site.y,
                    indiv.genome,
                    indiv.mass,
                    indiv.collected_on,
                ]
            )
        return output.getvalue()


def specimens_generate(
    params: SpecimenParams, grid: Grid | None = None
) -> AllSpecimens:
    """Generate specimens with random genomes and masses.

    Each genome is a string of bases of the same length. One locus is
    randomly chosen as "significant", and a specific mutation there
    predisposes the snail to mass changes.

    The process follows these steps:
    1. Generate genomes with random mutations
    2. Assign initial masses based on whether they have the significant mutation
    3. Place specimens randomly on the grid (no two snails in the same cell)
    4. Adjust masses based on location if a grid is provided

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
    identifiers = _make_idents(params.number)
    collection_dates = _make_collection_dates(params)
    masses = _make_initial_masses(params, genomes, susc_loc, susc_base)

    individuals = [
        Specimen(genome=g, mass=m, site=Point(), ident=i, collected_on=d)
        for g, m, i, d in zip(genomes, masses, identifiers, collection_dates)
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
        _place_specimens_on_grid(grid, result)
        _adjust_masses_by_location(grid, result, params.mut_scale)

    return result


def _adjust_masses_by_location(
    grid: Grid,
    specimens: AllSpecimens,
    mut_scale: float,
    specific_index: int | None = None,
) -> None:
    """Adjust mass based on grid values and genetic susceptibility.

    For each specimen, if the cell value is non-zero and the genome is
    susceptible, modify the mass. Specimens must already have site
    coordinates assigned by _place_specimens_on_grid().

    Parameters:
        grid: A Grid object containing pollution values
        specimens: An AllSpecimens object with individuals to potentially adjust
        mut_scale: Scaling factor for mutation effect
        specific_index: Optional index to adjust only a specific specimen
    """
    susc_locus = specimens.susceptible_locus
    susc_base = specimens.susceptible_base

    if specific_index is None:
        individuals = specimens.individuals
    else:
        individuals = [specimens.individuals[specific_index]]

    for indiv in individuals:
        assert indiv.site.x is not None and indiv.site.y is not None, (
            "Specimens must be placed on grid first"
        )
        x, y = indiv.site.x, indiv.site.y
        if grid.grid[x][y] > 0 and indiv.genome[susc_locus] == susc_base:
            indiv.mass = _mutate_mass(indiv.mass, mut_scale, grid.grid[x][y])


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


def _make_collection_dates(params: SpecimenParams) -> list[date]:
    """Generate random collection dates for specimens.

    Parameters:
        params: SpecimenParams with start_date, end_date, and number attributes

    Returns:
        List of randomly generated collection dates between start_date and end_date
    """
    start_ordinal = params.start_date.toordinal()
    end_ordinal = params.end_date.toordinal()
    return [
        date.fromordinal(random.randint(start_ordinal, end_ordinal))
        for _ in range(params.number)
    ]


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


def _make_initial_masses(
    params: SpecimenParams,
    genomes: list[str],
    susceptible_locus: int,
    susceptible_base: str,
) -> list[float]:
    """Generate initial masses for specimens based on significant mutation.

    Specimens with the susceptible base at the susceptible locus are given
    a higher initial mass range compared to non-susceptible specimens.

    Parameters:
        params: SpecimenParams with min_mass and max_mass attributes
        genomes: List of genome strings
        susceptible_locus: Position that determines susceptibility
        susceptible_base: Base that makes a specimen susceptible

    Returns:
        List of generated mass values between min_mass and max_mass,
        rounded to PRECISION decimal places
    """
    # Calculate mass range midpoint
    midpoint = (params.max_mass + params.min_mass) / 2

    # Create masses based on susceptibility
    masses = []
    for genome in genomes:
        if genome[susceptible_locus] == susceptible_base:
            # Susceptible specimens get higher mass range
            mass = round(random.uniform(midpoint, params.max_mass), utils.PRECISION)
        else:
            # Non-susceptible specimens get lower mass range
            mass = round(random.uniform(params.min_mass, midpoint), utils.PRECISION)
        masses.append(mass)

    return masses


def _make_locations(size: int, num: int) -> list[tuple[int, int]]:
    """Generate non-overlapping locations for specimens.

    Selects random locations from the grid, ensuring no two specimens
    are placed in the same cell. This implements the requirement that
    no two snails may be placed in the same cell.

    Parameters:
        size: Size of the grid (assuming square grid)
        num: Number of locations to generate

    Returns:
        List of (x, y) coordinate tuples

    Raises:
        ValueError: If there are not enough cells to place all specimens
    """
    if num > size * size:
        utils.fail(f"Cannot place {num} specimens on a {size}x{size} grid")

    # Create all possible grid locations
    all_locations = [(x, y) for x in range(size) for y in range(size)]

    # Select locations randomly without replacement
    chosen_locations = random.sample(all_locations, num)

    return chosen_locations


def _make_loci(params: SpecimenParams) -> list[int]:
    """Make a list of mutable loci positions.

    Parameters:
        params: SpecimenParams with length and mutations attributes

    Returns:
        A list of unique randomly selected positions that can be mutated
    """
    return random.sample(list(range(params.length)), params.mutations)


def _make_reference_genome(params: SpecimenParams) -> str:
    """Make a random reference genome.

    Parameters:
        params: SpecimenParams with length attribute

    Returns:
        A randomly generated genome string of the specified length
    """
    return "".join(random.choices(BASES, k=params.length))


def _mutate_mass(original: float, mut_scale: float, cell_value: float) -> float:
    """Mutate a single specimen's mass.

    Parameters:
        original: The original mass value
        mut_scale: Scaling factor for mutation effect
        cell_value: The grid cell value affecting the mutation

    Returns:
        The mutated mass value, rounded to PRECISION decimal places
    """
    return round(original * (1 + (mut_scale * cell_value)), utils.PRECISION)


def _place_specimens_on_grid(
    grid: Grid,
    specimens: AllSpecimens,
) -> None:
    """Place specimens randomly on the grid, ensuring no two share the same cell.

    Updates the site coordinates for each specimen.

    Parameters:
        grid: A Grid object containing pollution values
        specimens: An AllSpecimens object with individuals to place on the grid
    """
    grid_size = len(grid.grid)
    locations = _make_locations(grid_size, len(specimens.individuals))

    for indiv, (x, y) in zip(specimens.individuals, locations):
        indiv.site.x = x
        indiv.site.y = y
