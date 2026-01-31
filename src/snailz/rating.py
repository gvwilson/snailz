"""Ratings on machinery."""

from dataclasses import dataclass
import itertools
import random
from typing import ClassVar, Self

from ._base_mixin import BaseMixin
from ._utils import ForeignKeysType
from .machine import Machine
from .parameters import Parameters
from .person import Person


@dataclass
class Rating(BaseMixin):
    """
    A person's rating on a machine.

    Attributes:
        person_id: person identifier (in persons)
        machine_id: machine identifier (in machines)
        certified: whether person is certified on machine
    """

    table_name: ClassVar[str] = "rating"
    foreign_keys: ForeignKeysType = [
        ("person_id", "person", "ident"),
        ("machine_id", "machine", "ident"),
    ]

    person_id: str = ""
    machine_id: str = ""
    certified: bool = False

    @classmethod
    def make(
        cls, params: Parameters, persons: list[Person], machines: list[Machine]
    ) -> list[Self]:
        """Construct multiple ratings.

        Args:
            params: Data generation parameters.
            persons: list of people who have ratings.
            machines: list of machines that people are rated for.

        Returns:
            List of ratings.
        """

        num = max(1, int(params.ratings_frac * len(persons) * len(machines)))
        possible = list(itertools.product(persons, machines))
        actual = random.sample(possible, k=num)
        return [
            Rating(
                person_id=p.ident,
                machine_id=m.ident,
                certified=(random.random() < params.p_certified),
            )
            for (p, m) in actual
        ]
