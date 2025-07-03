"""Represent scientific staff."""

import random
from typing import ClassVar

import faker
from pydantic import BaseModel, Field

from . import utils


class Person(BaseModel):
    """A single person."""

    id_stem: ClassVar[str] = "P"
    id_digits: ClassVar[int] = 4

    id: str = Field(min_length=1, description="unique identifier")
    family: str = Field(min_length=1, description="family name")
    personal: str = Field(min_length=1, description="personal name")

    @staticmethod
    def make(params):
        """Make a person."""

        utils.ensure_id_generator(Person)
        if not hasattr(Person, "_fake"):
            Person._fake = faker.Faker(params.locale)
            Person._fake.seed_instance(random.randint(0, 1_000_000))

        return Person(
            id=next(Person._id_gen),
            family=Person._fake.last_name(),
            personal=Person._fake.first_name(),
        )

    @staticmethod
    def csv_header():
        """Generate header for CSV file."""

        return "id,family,personal"

    def __str__(self):
        """Convert to CSV string."""

        return f"{self.id},{self.family},{self.personal}"
