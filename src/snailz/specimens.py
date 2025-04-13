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
        susc_base = utils.choose_one(list(set(utils.BASES) - {reference[susc_locus]}))
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
            temp = [
                _make_specimen(params, specimens, survey, next(gen))
                for _ in range(model.specimens_num_per_survey(params, survey))
            ]
            model.specimens_place(survey, temp)
            for s in temp:
                s.mass = round(model.specimen_adjust_mass(survey, max_pollution, s), utils.PRECISION)
            specimens.items.extend(temp)

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
    specimens: AllSpecimens,
    survey: Survey,
    ident: str,
) -> Specimen:
    """Make a single specimen.

    Parameters:
        params: specimen parameters
        survey: survey this specimen is from
        ident: specimen identifier

    Returns:
        A randomly-generated specimen.
    """
    collected = model.specimen_collection_date(survey)
    genome = model.specimen_genome(specimens)
    is_mutant = genome[specimens.susc_locus] == specimens.susc_base

    mass = model.specimen_initial_mass(params, collected, is_mutant)
    return Specimen(
        ident=ident,
        survey_id=survey.ident,
        collected=collected,
        genome=genome,
        is_mutant=is_mutant,
        location=Point(x=0, y=0),
        mass=mass,
    )


def _specimen_id_generator() -> str:
    """Specimen ID generation function.

    Returns:
        Candidate ID for a specimen.
    """
    return "".join(random.choices(string.ascii_uppercase, k=6))
