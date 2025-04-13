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
    species: int = Field(description="species this snail belongs to")
    location: Point = Field(description="where specimen was collected")
    collected: date = Field(description="date when specimen was collected")
    genome: str = Field(description="bases in genome")
    mass: float = Field(default=0.0, ge=0, description="specimen mass in grams")
    is_mutant: bool = Field(default=False, description="is this specimen a mutant?")


class AllSpecimens(BaseModel):
    """A set of generated specimens."""

    loci: list[list[int]] = Field(description="locations where mutations can occur")
    references: list[str] = Field(description="unmutated genomes of each species")
    susc_base: str = Field(description="mutant base that induces mass changes")
    susc_locus: int = Field(ge=0, description="location of mass change mutation")
    items: list[Specimen] = Field(description="list of individual specimens")

    def to_csv(self, full: bool = False) -> str:
        """Return a CSV string representation of the specimen data.

        Parameters:
            full: include mutant and species information

        Returns:
            A CSV-formatted string.
        """
        if full:
            return utils.to_csv(
                self.items,
                [
                    "ident",
                    "survey",
                    "x",
                    "y",
                    "collected",
                    "genome",
                    "mass",
                    "mutant",
                    "species",
                ],
                lambda s: [
                    s.ident,
                    s.survey_id,
                    s.location.x if s.location.x >= 0 else None,
                    s.location.y if s.location.y >= 0 else None,
                    s.collected.isoformat(),
                    s.genome,
                    s.mass,
                    s.is_mutant,
                    s.species,
                ],
            )
        else:
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

        num_species = len(params.prob_species)
        references = [
            model.specimen_reference_genome(params) for _ in range(num_species)
        ]
        loci = [model.mutation_loci(params) for _ in range(num_species)]
        susc_locus = utils.choose_one(loci[0])
        susc_base = utils.choose_one(
            list(set(utils.BASES) - {references[0][susc_locus]})
        )
        gen = utils.unique_id("specimen", _specimen_id_generator)

        specimens = AllSpecimens(
            references=references,
            loci=loci,
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
                s.mass = round(
                    model.specimen_adjust_mass(survey, max_pollution, s),
                    utils.PRECISION,
                )
            specimens.items.extend(temp)

        return specimens


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
    species, genome = model.specimen_genome(params, specimens)
    is_mutant = (species == 0) and (genome[specimens.susc_locus] == specimens.susc_base)

    mass = model.specimen_initial_mass(params, species, collected, is_mutant)
    return Specimen(
        ident=ident,
        survey_id=survey.ident,
        species=species,
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
