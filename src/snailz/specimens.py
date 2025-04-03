"""Generate specimens."""

from datetime import date
import math
import random
import string

from pydantic import BaseModel, Field, model_validator

from . import utils
from .grids import Point


# Bases.
BASES = "ACGT"


class SpecimenParams(BaseModel):
    """Parameters for specimen generation."""

    length: int = Field(
        default=20, gt=0, description="Length of specimen genomes (must be positive)"
    )
    max_mass: float = Field(
        default=10.0, gt=0, description="Maximum mass for specimens (must be positive)"
    )
    num_mutations: int = Field(
        default=5,
        ge=0,
        description="Number of mutations in specimens (must be between 0 and length)",
    )
    spacing: float = Field(
        default=utils.DEFAULT_GRID_SIZE / 4.0,
        ge=0,
        description="Inter-specimen spacing",
    )
    start_date: date = Field(
        default=date.fromisoformat("2024-03-01"),
        description="Start date for specimen collection",
    )
    end_date: date = Field(
        default=date.fromisoformat("2024-04-30"),
        description="End date for specimen collection",
    )

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_fields(self):
        """Validate requirements on fields."""
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return self


class Specimen(BaseModel):
    """A single specimen."""

    ident: str = Field(description="unique identifier")
    collected: date = Field(description="date when specimen was collected")
    genome: str = Field(description="bases in genome")
    location: Point = Field(description="where specimen was collected")
    mass: float = Field(gt=0, description="specimen mass in grams")


class SpecimenList(BaseModel):
    """A set of generated specimens."""

    loci: list[int] = Field(description="locations where mutations can occur")
    reference: str = Field(description="unmutated genome")
    susc_base: str = Field(description="mutant base that induces mass changes")
    susc_locus: int = Field(ge=0, description="location of mass change mutation")
    specimens: list[Specimen] = Field(description="list of individual specimens")

    def to_csv(self) -> str:
        """Return a CSV string representation of the specimen data.

        Returns:
            A CSV-formatted string with people data (without parameters)
        """
        return utils.to_csv(
            self.specimens,
            ["ident", "genome", "x", "y", "mass"],
            lambda s: [s.ident, s.genome, s.location.x, s.location.y, s.mass],
        )


def specimens_generate(params: SpecimenParams, grid_id: str, grid_size: int) -> SpecimenList:
    """Generate a set of specimens."""

    positions = _place_specimens(grid_size, params.spacing)
    reference = _make_reference_genome(params)
    loci = _make_loci(params)
    susc_locus = random.choices(loci, k=1)[0]
    susc_base = reference[susc_locus]
    gen = utils.UniqueIdGenerator("specimen", _specimen_id_generator)
    return SpecimenList(
        loci=loci,
        reference=reference,
        susc_base=susc_base,
        susc_locus=susc_locus,
        specimens=[
            _make_specimen(params, reference, loci, gen, positions[i], grid_id)
            for i in range(len(positions))
        ],
    )


def _make_loci(params: SpecimenParams) -> list[int]:
    """Make a list of mutable loci positions.

    Parameters:
        params: SpecimenParams with length and mutations attributes

    Returns:
        A list of unique randomly selected positions that can be mutated
    """
    return list(sorted(random.sample(list(range(params.length)), params.num_mutations)))


def _make_reference_genome(params: SpecimenParams) -> str:
    """Make a random reference genome.

    Parameters:
        params: SpecimenParams with length attribute

    Returns:
        A randomly generated genome string of the specified length
    """
    return "".join(random.choices(BASES, k=params.length))


def _make_specimen(
    params: SpecimenParams,
    reference: str,
    loci: list,
    gen: utils.UniqueIdGenerator,
    location: Point,
    grid_id: str,
) -> Specimen:
    """Make a single specimen."""
    genome = list(reference)
    num_mutations = random.randint(1, len(loci))
    for loc in random.sample(range(len(loci)), num_mutations):
        candidates = list(sorted(set(BASES) - set(reference[loc])))
        genome[loc] = candidates[random.randrange(len(candidates))]
    genome = "".join(genome)

    start_ord = params.start_date.toordinal()
    end_ord = params.end_date.toordinal()
    collected = date.fromordinal(random.randint(start_ord, end_ord))

    return Specimen(
        ident=gen.next(grid_id),
        collected=collected,
        genome=genome,
        location=location,
        mass=random.uniform(params.max_mass / 4.0, params.max_mass)
    )


def _calculate_span(size: int, coord: int, span: int) -> range:
    return range(max(0, coord - span), 1 + min(size, coord + span))


def _place_specimens(size: int, spacing: float) -> list[Point]:
    """Generate locations for specimens.

    - Initialize a set of all possible (x, y) points.
    - Repeatedly choose one at random and add to the result.
    - Remove all points within a random radius of that point.
    """

    available = {(x, y) for x in range(size) for y in range(size)}
    result = []
    while available:
        loc = random.choices(list(available), k=1)[0]
        result.append(loc)
        radius = random.uniform(spacing / 4, spacing)
        span = math.ceil(radius)
        for x in _calculate_span(size, loc[0], span):
            for y in _calculate_span(size, loc[1], span):
                available.discard((x, y))
    return [Point(x=r[0], y=r[1]) for r in result]


def _specimen_id_generator(grid_id: str) -> str:
    return f"{grid_id}-{''.join(random.choices(string.ascii_uppercase, k=6))}"
