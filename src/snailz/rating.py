"""Ratings on machinery."""

from dataclasses import dataclass
import itertools
import random
from typing import ClassVar
from ._base_mixin import BaseMixin


RATINGS = {
    "novice": 0.7,
    "expert": 0.3,
}


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
    def make(cls, params, persons, machines, *, rand=random):
        """Generate ratings."""

        num = max(1, int(params.ratings_frac * len(persons) * len(machines)))
        values = list(RATINGS.keys())
        weights = list(RATINGS.values())
        ratings = rand.choices(values, weights=weights, k=num)
        return [
            Rating(person_id=p.ident, machine_id=m.ident, rating=r)
            for ((p, m), r) in zip(itertools.product(persons, machines), ratings)
        ]
