"""Ratings on machinery."""

from dataclasses import dataclass
import itertools
import random
from typing import ClassVar
from .utils import BaseMixin


RATINGS = {
    "novice": 0.7,
    "expert": 0.3,
}

RATINGS_FRAC = 2


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
    rating: str | None = None

    @classmethod
    def make(cls, persons, machines, *, rand=random):
        """Generate ratings."""

        num = max(1, len(persons) * len(machines) // RATINGS_FRAC)
        values = list(RATINGS.keys())
        weights = list(RATINGS.values())
        ratings = rand.choices(values, weights=weights, k=num)
        return [
            Rating(person_id=p.ident, machine_id=m.ident, rating=r)
            for ((p, m), r) in zip(itertools.product(persons, machines), ratings)
        ]
