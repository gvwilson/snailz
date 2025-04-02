"""Represent snailz parameters with default values."""

import csv
import io

from faker import config as faker_config
from pydantic import BaseModel, Field, field_validator


class PersonParams(BaseModel):
    """Parameters for people generation."""

    locale: str = Field(default="et_EE", description="Locale for names")
    number: int = Field(default=5, gt=0, description="Number of people")

    model_config = {"extra": "forbid"}

    @field_validator("locale")
    def validate_fields(cls, v):
        """Validate that the locale is available in faker."""
        if v not in faker_config.AVAILABLE_LOCALES:
            raise ValueError(f"Unknown locale {v}")
        return v


class Person(BaseModel):
    """A single person."""

    ident: str = Field(description="unique identifier")
    family: str = Field(description="family name")
    personal: str = Field(description="personal name")


class PersonList(BaseModel):
    """A set of generated people."""

    persons: list[Person] = Field(description="all persons")

    def to_csv(self):
        """Create a CSV representation of the people data.

        Returns:
            A CSV-formatted string with people data.
        """
        return _to_csv(
            self.persons,
            ["ident", "personal", "family"],
            lambda person: [person.ident, person.personal, person.family],
        )


# ----------------------------------------------------------------------


class AllParams(BaseModel):
    """Represent all parameters combined."""

    seed: int = Field(default=7493418, ge=0, description="RNG seed")
    person: PersonParams = Field(
        default=PersonParams(), description="parameters for people generation"
    )


class AllData(BaseModel):
    """Represent all generated data combined."""

    params: AllParams = Field(description="all parameters")
    persons: PersonList = Field(description="all persons")


# ----------------------------------------------------------------------


def _to_csv(rows, fields, f_make_row):
    """Generic converter from list of models to CSV string."""

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(fields)
    for r in rows:
        writer.writerow(f_make_row(r))
    return output.getvalue()
