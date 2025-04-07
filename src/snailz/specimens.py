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
    p_missing_location: float = Field(
        default=0.05, ge=0, description="Probability that location is missing"
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
                s.location.x if s.location.x >= 0 else None,
                s.location.y if s.location.y >= 0 else None,
                s.collected.isoformat(),
                s.genome,
                s.mass,
            ],
        )


def specimens_generate(params: SpecimenParams, surveys: AllSurveys) -> AllSpecimens:
    """Generate a set of specimens.

    Parameters:
        params: specimen generation parameters
        surveys: surveys to generate specimens for

    Returns:
        A set of surveys.
    """

    reference = _make_reference_genome(params)
    loci = _make_loci(params)
    susc_locus = random.choices(loci, k=1)[0]
    susc_base = reference[susc_locus]
    gen = utils.unique_id("specimen", _specimen_id_generator)
    specimens = AllSpecimens(
        loci=loci,
        reference=reference,
        susc_base=susc_base,
        susc_locus=susc_locus,
        items=[],
    )

    max_value = surveys.max_value()
    for survey in surveys.items:
        positions = _place_specimens(params, survey.size)
        for pos in positions:
            ident = next(gen)
            specimens.items.append(
                _make_specimen(params, survey, specimens, ident, pos, max_value)
            )

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
    ident: str,
    location: Point,
    max_value: float,
) -> Specimen:
    """Make a single specimen.

    Parameters:
        params: specimen parameters
        survey: survey this specimen is from
        specimens: all specimens in this survey
        gen: unique ID generation function
        location: grid point where specimen was sampled
        max_value: maximum pollution value across all surveys

    Returns:
        A randomly-generated specimen.
    """
    # Collection date
    collected = date.fromordinal(
        random.randint(survey.start_date.toordinal(), survey.end_date.toordinal())
    )

    # Mutated genome
    genome = list(specimens.reference)
    num_mutations = random.randint(1, len(specimens.loci))
    for loc in random.sample(range(len(specimens.loci)), num_mutations):
        candidates = list(sorted(set(BASES) - set(specimens.reference[loc])))
        genome[loc] = candidates[random.randrange(len(candidates))]
    genome = "".join(genome)

    # Mutant status
    is_mutant = genome[specimens.susc_locus] == specimens.susc_base

    # Mass
    mass_scale = params.mut_mass_scale if is_mutant else 1.0
    max_mass = mass_scale * params.max_mass
    mass = round(random.uniform(max_mass / 2.0, max_mass), utils.PRECISION)
    assert survey.cells is not None  # for type checking

    # Pollution effects if location known
    if (location.x >= 0) and (location.y >= 0):
        pollution_scaling = 1.0 + 2.0 * utils.sigmoid(
            survey.cells[location.x, location.y] / max_value
        )
        mass *= pollution_scaling

    return Specimen(
        ident=ident,
        survey_id=survey.ident,
        collected=collected,
        genome=genome,
        location=location,
        mass=mass,
        is_mutant=is_mutant,
    )


def _calculate_span(size: int, coord: int, span: int) -> range:
    """
    Calculate axial range of cells close to a center point.

    Parameters:
        size: grid size
        coord: X or Y coordinate
        span: maximum width on either side

    Returns:
        Endpoint coordinates of span.
    """
    return range(max(0, coord - span), 1 + min(size, coord + span))


def _place_specimens(params: SpecimenParams, size: int) -> list[Point]:
    """Generate locations for specimens.

    - Initialize a set of all possible (x, y) points.
    - Repeatedly choose one at random and add to the result.
    - Remove all points within a random radius of that point.

    Parameters:
        params: specimen generation parameters
        size: grid size

    Returns:
        A list of specimen locations.
    """

    # Generate points by repeated spatial subtraction.
    available = {(x, y) for x in range(size) for y in range(size)}
    result = []
    while available:
        loc = random.choices(list(available), k=1)[0]
        result.append(loc)
        radius = random.uniform(params.spacing / 4, params.spacing)
        span = math.ceil(radius)
        for x in _calculate_span(size, loc[0], span):
            for y in _calculate_span(size, loc[1], span):
                available.discard((x, y))

    # Replace some points with markers for missing data
    missing = Point(x=-1, y=-1)
    return [
        missing
        if random.uniform(0.0, 1.0) < params.p_missing_location
        else Point(x=r[0], y=r[1])
        for r in result
    ]


def _specimen_id_generator() -> str:
    """Specimen ID generation function.

    Returns:
        Candidate ID for a specimen.
    """
    return "".join(random.choices(string.ascii_uppercase, k=6))
