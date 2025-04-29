"""Generate random persons."""

import random

import faker
from pydantic import BaseModel, Field

from .parameters import PersonParams
from . import utils


class Person(BaseModel):
    """A single person."""

    ident: str = Field(description="unique identifier")
    family: str = Field(description="family name")
    personal: str = Field(description="personal name")

    model_config = {"extra": "forbid"}


class AllPersons(BaseModel):
    """A set of generated people."""

    items: list[Person] = Field(description="all persons")

    model_config = {"extra": "forbid"}

    def to_csv(self) -> str:
        """Create a CSV representation of the people data.

        Returns:
            A CSV-formatted string with people data.
        """
        return utils.to_csv(
            self.items,
            ["ident", "personal", "family"],
            lambda p: [p.ident, p.personal, p.family],
        )

    @staticmethod
    def generate(params: PersonParams) -> "AllPersons":
        """Generate random persons.

        Parameters:
            params: Data generation parameters.

        Returns:
            Data model including all persons.
        """
        fake = faker.Faker(params.locale)
        fake.seed_instance(random.randint(0, 1_000_000))
        id_gen = utils.unique_id("person", _person_id_generator)
        items = []
        for _ in range(params.number):
            family = fake.last_name()
            personal = fake.first_name()
            ident = id_gen.send((family, personal))
            items.append(
                Person(
                    ident=ident,
                    family=family,
                    personal=personal,
                )
            )

        return AllPersons(items=items)


def _person_id_generator(family: str, personal: str) -> str:
    """Generate unique ID for a person.

    Parameters:
        family: Person's family name.
        personal: Person's personal name.

    Returns:
        Candidate identifier 'CCNNNN'.
    """
    f = family[0].lower()
    p = personal[0].lower()
    num = random.randint(0, 9999)
    return f"{f}{p}{num:04d}"
