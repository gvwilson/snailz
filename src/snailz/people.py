"""Generate synthetic people."""

import csv
import io
import random

from faker import Faker, config as faker_config
from pydantic import BaseModel, Field, field_validator

from . import utils


class PeopleParams(BaseModel):
    """Parameters for people generation.

    - locale: Locale code for generating names (must be supported by Faker)
    - number: Number of people to generate (must be positive)
    - seed: Random seed for reproducibility
    """

    locale: str = Field()
    number: int = Field(gt=0)
    seed: int = Field()

    @field_validator("locale")
    def validate_locale(cls, v):
        """Validate that the locale is available in faker."""
        if v not in faker_config.AVAILABLE_LOCALES:
            raise ValueError(f"Unknown locale {v}")
        return v

    model_config = {"extra": "forbid"}


class Person(BaseModel):
    """A single person.

    - family: family name
    - ident: unique identifier
    - personal: personal name
    """

    family: str
    ident: str
    personal: str


class AllPersons(BaseModel):
    """A set of generated people.

    - individuals: list of people
    - params: parameters used to generate this data
    """

    individuals: list[Person]
    params: PeopleParams

    def to_csv(self) -> str:
        """Return a CSV string representation of the people data.

        Returns:
            A CSV-formatted string with people data (without parameters) using Unix line endings
        """
        output = io.StringIO()
        writer = csv.writer(output, **utils.CSV_SETTINGS)
        writer.writerow(["ident", "personal", "family"])
        for person in self.individuals:
            writer.writerow([person.ident, person.personal, person.family])
        return output.getvalue()


def people_generate(params: PeopleParams) -> AllPersons:
    """Generate synthetic people data.

    Parameters:
        params: PeopleParams object

    Returns:
        AllPersons object containing generated individuals and parameters
    """
    fake = Faker(params.locale)
    fake.seed_instance(params.seed)
    gen = utils.UniqueIdGenerator(
        "people",
        lambda p, f: f"{f[0].lower()}{p[0].lower()}{random.randint(0, 9999):04d}",
    )

    individuals = []
    for _ in range(params.number):
        personal = fake.first_name()
        family = fake.last_name()
        ident = gen.next(personal, family)
        individuals.append(Person(personal=personal, family=family, ident=ident))

    return AllPersons(individuals=individuals, params=params)
