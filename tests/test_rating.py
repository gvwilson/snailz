"""Test person-machine ratings."""

import itertools

from snailz import Machine, Parameters, Person, Rating


def test_rating_model_fields():
    r = Rating(person_id="p1", machine_id="m1", certified=True)
    assert r.person_id == "p1"
    assert r.machine_id == "m1"
    assert r.certified


def test_rating_make_for_every_pair():
    params = Parameters(ratings_frac=1.0, p_certified=1.0)
    persons = [Person(family="A", personal="B"), Person(family="C", personal="D")]
    machines = [Machine(name="some machine")]
    ratings = Rating.make(params, persons, machines)
    assert len(ratings) == len(persons) * len(machines)
    expected = {(p.ident, m.ident) for p, m in itertools.product(persons, machines)}
    actual = {(r.person_id, r.machine_id) for r in ratings}
    assert actual == expected
    assert all(r.certified for r in ratings)
