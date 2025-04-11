"""Generate specimens."""

from datetime import date
import random
import string

from pydantic import BaseModel, Field

from .grid import Point
from .parameters import SpecimenParams
from .surveys import Survey, AllSurveys
from . import model, utils


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
            A CSV-formatted string.
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

    @staticmethod
    def generate(params: SpecimenParams, surveys: AllSurveys) -> "AllSpecimens":
        """Generate a set of specimens.

        Parameters:
            params: specimen generation parameters
            surveys: surveys to generate specimens for

        Returns:
            A set of surveys.
        """

        reference = _make_reference_genome(params)
        loci = model.mutation_loci(params)
        susc_locus = utils.choose_one(loci)
        susc_base = reference[susc_locus]
        gen = utils.unique_id("specimen", _specimen_id_generator)
        specimens = AllSpecimens(
            loci=loci,
            reference=reference,
            susc_base=susc_base,
            susc_locus=susc_locus,
            items=[],
        )

        max_pollution = surveys.max_pollution()
        for survey in surveys.items:
            positions = model.specimen_locations(params, survey.size)
            for pos in positions:
                ident = next(gen)
                specimens.items.append(
                    _make_specimen(params, survey, specimens, ident, pos, max_pollution)
                )

        return specimens


def _make_reference_genome(params: SpecimenParams) -> str:
    """Make a random reference genome.

    Parameters:
        params: SpecimenParams with length attribute

    Returns:
        A randomly generated genome string of the specified length
    """
    return "".join(random.choices(utils.BASES, k=params.length))


def _make_specimen(
    params: SpecimenParams,
    survey: Survey,
    specimens: AllSpecimens,
    ident: str,
    location: Point,
    max_pollution: float,
) -> Specimen:
    """Make a single specimen.

    Parameters:
        params: specimen parameters
        survey: survey this specimen is from
        specimens: all specimens in this survey
        ident: specimen identifier
        location: grid point where specimen was sampled
        max_pollution: maximum pollution value across all surveys

    Returns:
        A randomly-generated specimen.
    """
    collected = model.specimen_collection_date(survey)
    genome = model.specimen_genome(specimens)
    is_mutant = genome[specimens.susc_locus] == specimens.susc_base

    assert survey.cells is not None  # for type checking
    pollution_level = (
        survey.cells[location.x, location.y]
        if (location.x >= 0) and (location.y >= 0)
        else None
    )

    mass = model.specimen_mass(
        params, max_pollution, collected, pollution_level, is_mutant
    )
    return Specimen(
        ident=ident,
        survey_id=survey.ident,
        collected=collected,
        genome=genome,
        is_mutant=is_mutant,
        location=location,
        mass=round(mass, utils.PRECISION),
    )


def _specimen_id_generator() -> str:
    """Specimen ID generation function.

    Returns:
        Candidate ID for a specimen.
    """
    return "".join(random.choices(string.ascii_uppercase, k=6))
