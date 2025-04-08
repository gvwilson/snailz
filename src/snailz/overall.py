"""Represent snailz parameters."""

from pydantic import BaseModel, Field

from .assays import AssayParams, AllAssays
from .machines import MachineParams, AllMachines
from .persons import PersonParams, AllPersons
from .specimens import SpecimenParams, AllSpecimens
from .surveys import SurveyParams, AllSurveys


class AllParams(BaseModel):
    """Represent all parameters combined."""

    seed: int = Field(default=7493418, ge=0, description="RNG seed")
    machine: MachineParams = Field(
        default=MachineParams(), description="parameters for machine generation"
    )
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

    @staticmethod
    def generate(params: AllParams) -> "AllData":
        """Generate and save all data."""
        machines = AllMachines.generate(params.machine)
        surveys = AllSurveys.generate(params.survey)
        persons = AllPersons.generate(params.person)
        specimens = AllSpecimens.generate(params.specimen, surveys)
        assays = AllAssays.generate(params.assay, persons, machines, specimens)
        return AllData(
            assays=assays,
            machines=machines,
            params=params,
            persons=persons,
            specimens=specimens,
            surveys=surveys,
        )
