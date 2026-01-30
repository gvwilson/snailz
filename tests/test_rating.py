"""Test person-machine ratings."""

import itertools

from snailz import Machine, Parameters, Person, Rating


class RandChoice:
    def __init__(self, *values):
        self.values = values

    def choices(self, *args, **kwargs):
        result = []
        for i in range(kwargs["k"]):
            result.append(self.values[i % len(self.values)])
        return result


def test_rating_model_fields():
    r = Rating(person_id="p1", machine_id="m1", rating="novice")
    assert r.person_id == "p1"
    assert r.machine_id == "m1"
    assert r.rating == "novice"


def test_make_ratings_for_every_pair():
    params = Parameters(ratings_frac=1.0)
    persons = [Person(family="A", personal="B"), Person(family="C", personal="D")]
    machines = [Machine(name="some machine")]
    ratings = Rating.make(params, persons, machines, rand=RandChoice("novice"))
    expected = {(p.ident, m.ident) for p, m in itertools.product(persons, machines)}
    actual = {(r.person_id, r.machine_id) for r in ratings}
    assert actual == expected
    assert all(r.rating == "novice" for r in ratings)
