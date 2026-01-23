"""Represent scientific staff."""

import faker
from pydantic import BaseModel, ConfigDict, Field
import random
from typing import ClassVar

from . import utils


SUPERVISOR_RATIO = 3


class Person(BaseModel):
    """A single person."""

    id_stem: ClassVar[str] = "P"
    id_digits: ClassVar[int] = 4

    model_config = ConfigDict(
        json_schema_extra={
            "foreign_key": {
                "supervisor_id": ("person", "person_id"),
            }
        }
    )

    person_id: str = Field(
        min_length=1,
        description="unique identifier",
        json_schema_extra={"primary_key": True},
    )
    family: str = Field(min_length=1, description="family name")
    personal: str = Field(min_length=1, description="personal name")
    supervisor_id: str | None = Field(default=None, description="supervisor identifier")

    @staticmethod
    def make(params):
        """Make persons."""

        utils.ensure_id_generator(Person)
        if not hasattr(Person, "_fake"):
            Person._fake = faker.Faker(params.locale)
            Person._fake.seed_instance(random.randint(0, 1_000_000))

        staff = [
            Person(
                person_id=next(Person._id_gen),
                family=Person._fake.last_name(),
                personal=Person._fake.first_name(),
            )
            for _ in range(params.num_persons)
        ]

        num_supervisors = max(1, params.num_persons // SUPERVISOR_RATIO)
        supervisors = [
            Person(
                person_id=next(Person._id_gen),
                family=Person._fake.last_name(),
                personal=Person._fake.first_name(),
            )
            for _ in range(num_supervisors)
        ]

        for person in staff:
            person.supervisor_id = random.choice(supervisors).person_id

        if num_supervisors > 1:
            for person in supervisors[:-1]:
                person.supervisor_id = supervisors[-1].person_id

        return staff + supervisors

    @staticmethod
    def csv_header():
        """Generate header for CSV file."""

        return "person_id,family,personal"

    def __str__(self):
        """Convert to CSV string."""

        return f"{self.person_id},{self.family},{self.personal}"
