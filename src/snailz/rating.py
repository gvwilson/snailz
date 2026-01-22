"""Ratings on machinery."""

from pydantic import BaseModel, ConfigDict, Field
import random


RATINGS_FRACTION = 0.25


class Rating(BaseModel):
    """A person's rating on a kind of machine."""

    model_config = ConfigDict(
        json_schema_extra={
            "foreign_key": {
                "person_id": ("person", "person_id"),
                "machine_id": ("machine", "machine_id"),
            }
        }
    )

    person_id: str = Field(description="person ID")
    machine_id: str = Field(description="machine ID")
    rating: int | None = Field(description="rating")

    @staticmethod
    def make(persons, machines):
        """Generate ratings."""

        pairs = [(p, m) for p in persons for m in machines]
        num_ratings = int(RATINGS_FRACTION * len(pairs))
        ratings = [None, 1, 1, 1, 1, 2, 2, 2, 3, 3]
        return [
            Rating(
                person_id=p.person_id,
                machine_id=m.machine_id,
                rating=random.choice(ratings),
            )
            for p, m in random.sample(pairs, k=num_ratings)
        ]
