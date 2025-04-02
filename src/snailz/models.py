"""Represent snailz parameters with default values."""

import csv
import io

from faker import config as faker_config
from pydantic import BaseModel, Field, field_validator

# ----------------------------------------------------------------------

class GridParams(BaseModel):
    """Parameters for grid generation."""

    number: int = Field(default=3, gt=0, description="Number of grids")
    size: int = Field(default=15, gt=0, description="Grid size")

    model_config = {"extra": "forbid"}


class Grid(BaseModel):
    """A single grid."""

    ident: str = Field(description="grid identifier")
    cells: list[list] = Field(description="grid cells")
    size: int = Field(description="grid size")

    model_config = {"extra": "forbid"}

    def to_csv(self):
        """Create a CSV representation of a single grid.

        Returns:
            A CSV-formatted string with grid cells.
        """
        output = io.StringIO()
        for y in range(self.size - 1, -1, -1):
            temp = [f"{self.cells[x][y]}" for x in range(size)]
            print(",".join(temp), file=output)
        return output.getvalue()


class GridList(BaseModel):
    """A set of generated grids."""

    model_config = {"extra": "forbid"}

    grids: list[Grid] = Field(description="all grids")


# ----------------------------------------------------------------------


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

    model_config = {"extra": "forbid"}


class PersonList(BaseModel):
    """A set of generated people."""

    persons: list[Person] = Field(description="all persons")

    model_config = {"extra": "forbid"}

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
    grid: GridParams = Field(
        default=GridParams(), description="parameters for grid generation"
    )
    person: PersonParams = Field(
        default=PersonParams(), description="parameters for people generation"
    )

    model_config = {"extra": "forbid"}


class AllData(BaseModel):
    """Represent all generated data combined."""

    params: AllParams = Field(description="all parameters")
    persons: PersonList = Field(description="all persons")
    grids: GridList = Field(description="all grids")

    model_config = {"extra": "forbid"}


# ----------------------------------------------------------------------


def _to_csv(rows, fields, f_make_row):
    """Generic converter from list of models to CSV string."""

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(fields)
    for r in rows:
        writer.writerow(f_make_row(r))
    return output.getvalue()
