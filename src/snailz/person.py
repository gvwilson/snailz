"""Staff."""

from dataclasses import dataclass
from faker import Faker
import random
from typing import ClassVar, Self

from ._base_mixin import BaseMixin
from ._utils import IdGeneratorType, ForeignKeysType, id_generator, validate
from .parameters import Parameters


@dataclass
class Person(BaseMixin):
    """
    A single person.

    Attributes:
        ident: unique identifier
        family: family name
        personal: personal name
        supervisor_id: ident of supervisor (if any)
    """

    primary_key: ClassVar[str] = "ident"
    foreign_keys: ForeignKeysType = [("supervisor_id", "person", "ident")]
    nullable_keys: ClassVar[set[str]] = {"supervisor_id"}
    table_name: ClassVar[str] = "person"
    _next_id: IdGeneratorType = id_generator("P", 4)

    ident: str = ""
    family: str = ""
    personal: str = ""
    supervisor_id: str | None = None

    def __post_init__(self):
        """
        Validate fields and generate unique identifier.

        Raises:
            ValueError: If validation fails.
        """

        validate(self.ident == "", "person ID cannot be set externally")
        validate(len(self.family) > 0, "family name cannot be empty")
        validate(len(self.personal) > 0, "personal name cannot be empty")

        self.ident = next(self._next_id)

    @classmethod
    def make(cls, params: Parameters, fake: Faker) -> list[Self]:
        """
        Construct multiple persons, some of whom have other persons
        as supervisors.

        Args:
            params: Parameters object.
            fake: Name generator.

        Returns:
            List of persons.
        """

        num_supervisors = max(1, int(params.supervisor_frac * params.num_persons))
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
