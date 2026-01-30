"""Staff."""

from dataclasses import dataclass
import random
from typing import ClassVar, Generator
from .utils import BaseMixin, id_generator, validate


SUPERVISOR_FRACTION = 0.3


@dataclass
class Person(BaseMixin):
    """A single person."""

    primary_key: ClassVar[str] = "ident"
    foreign_keys: ClassVar[list[tuple[str, str, str]]] = [
        ("supervisor_id", "person", "ident")
    ]
    table_name: ClassVar[str] = "person"
    _next_id: ClassVar[Generator[str, None, None]] = id_generator("P", 4)

    ident: str = ""
    family: str = ""
    personal: str = ""
    supervisor_id: str | None = None

    def __post_init__(self):
        """Validate and fill in."""

        validate(self.ident == "", "person ID cannot be set externally")
        validate(len(self.family) > 0, "family name cannot be empty")
        validate(len(self.personal) > 0, "personal name cannot be empty")

        self.ident = next(self._next_id)

    @classmethod
    def make(cls, params, fake, supervisor_fraction=SUPERVISOR_FRACTION):
        """Make persons."""

        validate(params.num_persons > 0, "can only make positive number of persons")

        validate(supervisor_fraction >= 0.0, "require non-negative supervisor fraction")
        num_supervisors = max(1, int(supervisor_fraction * params.num_persons))
        num_staff = params.num_persons - num_supervisors

        staff = [
            cls(
                family=fake.last_name(),
                personal=fake.first_name(),
            )
            for _ in range(num_staff)
        ]

        supervisors = [
            cls(
                family=fake.last_name(),
                personal=fake.first_name(),
            )
            for _ in range(num_supervisors)
        ]

        for person in staff:
            person.supervisor_id = random.choice(supervisors).ident

        return staff + supervisors
