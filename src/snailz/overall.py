"""Represent snailz parameters."""

from pydantic import BaseModel, Field

from .assays import AssayParams, AllAssays, assays_generate
from .machines import AllMachines, machines_generate
from .persons import PersonParams, AllPersons, persons_generate
from .specimens import SpecimenParams, AllSpecimens, specimens_generate
from .surveys import SurveyParams, AllSurveys, surveys_generate


class AllParams(BaseModel):
    """Represent all parameters combined."""

    seed: int = Field(default=7493418, ge=0, description="RNG seed")
    num_machines: int = Field(default=5, gt=0, description="number of machines")
    assay: AssayParams = Field(
        default=AssayParams(), description="parameters for assay generation"
    )
    survey: SurveyParams = Field(
        default=SurveyParams(), description="parameters for survey generation"
    )
    person: PersonParams = Field(
        default=PersonParams(), description="parameters for people generation"
    )
    specimen: SpecimenParams = Field(
        default=SpecimenParams(),
        description="parameters for specimen generation",
    )

    model_config = {"extra": "forbid"}


class AllData(BaseModel):
    """Represent all generated data combined."""

    assays: AllAssays = Field(description="all assays")
    machines: AllMachines = Field(description="all machines")
    params: AllParams = Field(description="all parameters")
    persons: AllPersons = Field(description="all persons")
    specimens: AllSpecimens = Field(description="all specimens")
    surveys: AllSurveys = Field(description="all surveys")

    model_config = {"extra": "forbid"}


def all_generate(params: AllParams) -> AllData:
    """Generate and save all data."""
    machines = machines_generate(params.num_machines)
    surveys = surveys_generate(params.survey)
    persons = persons_generate(params.person)

    specimens = specimens_generate(params.specimen, surveys)

    assays = assays_generate(params.assay, persons, machines, specimens)

    return AllData(
        assays=assays,
        machines=machines,
        params=params,
        persons=persons,
        specimens=specimens,
        surveys=surveys,
    )
