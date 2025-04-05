"""Represent snailz parameters."""

from pydantic import BaseModel, Field

from .assays import AssayParams, AllAssays
from .surveys import SurveyParams, AllSurveys
from .persons import PersonParams, AllPersons
from .specimens import SpecimenParams, AllSpecimens


class AllParams(BaseModel):
    """Represent all parameters combined."""

    seed: int = Field(default=7493418, ge=0, description="RNG seed")
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
        default=SpecimenParams(), description="parameters for specimen generation"
    )

    model_config = {"extra": "forbid"}


class AllData(BaseModel):
    """Represent all generated data combined."""

    params: AllParams = Field(description="all parameters")
    assays: AllAssays = Field(description="all assays")
    surveys: AllSurveys = Field(description="all surveys")
    persons: AllPersons = Field(description="all persons")
    specimens: AllSpecimens = Field(description="all specimens")

    model_config = {"extra": "forbid"}
