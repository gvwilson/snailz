"""Generate random persons."""

import random

import faker
import faker.config
from pydantic import BaseModel, Field, field_validator

from . import utils


class PersonParams(BaseModel):
    """Parameters for people generation."""

    locale: str = Field(default="et_EE", description="Locale for names")
    number: int = Field(default=5, gt=0, description="Number of people")

    model_config = {"extra": "forbid"}

    @field_validator("locale")
    def validate_fields(cls, v):
        """Validate that the locale is available in faker."""
        if v not in faker.config.AVAILABLE_LOCALES:
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
        return utils.to_csv(
            self.persons,
            ["ident", "personal", "family"],
            lambda person: [person.ident, person.personal, person.family],
        )


def persons_generate(parameters):
    """Generate random persons."""
    fake = faker.Faker(parameters.locale)
    fake.seed_instance(random.randint(0, 1_000_000))
    gen = utils.UniqueIdGenerator("person", _person_id_generator)
    persons = []
    for _ in range(parameters.number):
        f = fake.last_name()
        p = fake.first_name()
        i = gen.next(f, p)
        persons.append(
            Person(
                ident=i,
                family=f,
                personal=p,
            )
        )

    return PersonList(persons=persons)


def _person_id_generator(family, personal):
    """Generate unique ID for a person (CCNNNN)."""
    f = family[0].lower()
    p = personal[0].lower()
    num = random.randint(0, 9999)
    return f"{f}{p}{num:04d}"
