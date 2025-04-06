"""Generate specimens."""

from datetime import date
import math
import random
import string

from pydantic import BaseModel, Field

from . import utils
from .grid import Point
from .surveys import Survey, AllSurveys


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
    mut_mass_scale: float = Field(
        default=2.0, gt=0, description="Scaling factor for mutant snail mass"
    )
    num_mutations: int = Field(
        default=5,
        ge=0,
        description="Number of mutations in specimens (must be between 0 and length)",
    )
    spacing: float = Field(
        default=utils.DEFAULT_SURVEY_SIZE / 4.0,
        ge=0,
        description="Inter-specimen spacing",
    )

    model_config = {"extra": "forbid"}


class Specimen(BaseModel):
    """A single specimen."""

    ident: str = Field(description="unique identifier")
    survey_id: str = Field(description="survey identifier")
    location: Point = Field(description="where specimen was collected")
    collected: date = Field(description="date when specimen was collected")
    genome: str = Field(description="bases in genome")
    mass: float = Field(default=0.0, ge=0, description="specimen mass in grams")
    is_mutant: bool = Field(default=False, description="is this specimen a mutant?")


class AllSpecimens(BaseModel):
    """A set of generated specimens."""

    loci: list[int] = Field(description="locations where mutations can occur")
    reference: str = Field(description="unmutated genome")
    susc_base: str = Field(description="mutant base that induces mass changes")
    susc_locus: int = Field(ge=0, description="location of mass change mutation")
    items: list[Specimen] = Field(description="list of individual specimens")

    def to_csv(self) -> str:
        """Return a CSV string representation of the specimen data.

        Returns:
            A CSV-formatted string with people data (without parameters)
        """
        return utils.to_csv(
            self.items,
            ["ident", "survey", "x", "y", "collected", "genome", "mass"],
            lambda s: [
                s.ident,
                s.survey_id,
                s.location.x,
                s.location.y,
                s.collected.isoformat(),
                s.genome,
                s.mass,
            ],
        )


def specimens_generate(params: SpecimenParams, surveys: AllSurveys) -> AllSpecimens:
    """Generate a set of specimens."""

    reference = _make_reference_genome(params)
    loci = _make_loci(params)
    susc_locus = random.choices(loci, k=1)[0]
    susc_base = reference[susc_locus]
    gen = utils.UniqueIdGenerator("specimen", _specimen_id_generator)
    specimens = AllSpecimens(
        loci=loci,
        reference=reference,
        susc_base=susc_base,
        susc_locus=susc_locus,
        items=[],
    )

    for survey in surveys.items:
        positions = _place_specimens(survey.size, params.spacing)
        for pos in positions:
            specimens.items.append(_make_specimen(params, survey, specimens, gen, pos))

    return specimens


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
    survey: Survey,
    specimens: AllSpecimens,
    gen: utils.UniqueIdGenerator,
    location: Point,
) -> Specimen:
    """Make a single specimen."""
    genome = list(specimens.reference)
    collected = date.fromordinal(
        random.randint(survey.start_date.toordinal(), survey.end_date.toordinal())
    )

    num_mutations = random.randint(1, len(specimens.loci))
    for loc in random.sample(range(len(specimens.loci)), num_mutations):
        candidates = list(sorted(set(BASES) - set(specimens.reference[loc])))
        genome[loc] = candidates[random.randrange(len(candidates))]
    genome = "".join(genome)

    is_mutant = genome[specimens.susc_locus] == specimens.susc_base
    mass_scale = params.mut_mass_scale if is_mutant else 1.0
    max_mass = mass_scale * params.max_mass
    mass = round(random.uniform(max_mass / 2.0, max_mass), utils.PRECISION)

    return Specimen(
        ident=gen.next(),
        survey_id=survey.ident,
        collected=collected,
        genome=genome,
        location=location,
        mass=mass,
        is_mutant=is_mutant,
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


def _specimen_id_generator() -> str:
    return "".join(random.choices(string.ascii_uppercase, k=6))
