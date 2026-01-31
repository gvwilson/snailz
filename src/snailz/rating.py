"""Ratings on machinery."""

from dataclasses import dataclass
import itertools
import random
from typing import ClassVar
from ._base_mixin import BaseMixin


@dataclass
class Rating(BaseMixin):
    """A person's rating on a machine."""

    table_name: ClassVar[str] = "rating"
    foreign_keys: ClassVar[list[tuple[str, str, str]]] = [
        ("person_id", "person", "ident"),
        ("machine_id", "machine", "ident"),
    ]

    person_id: str = ""
    machine_id: str = ""
    certified: bool = False

    @classmethod
    def make(cls, params, persons, machines):
        """Generate ratings."""

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
