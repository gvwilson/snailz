"""Generate random persons."""

import random

from faker import Faker

from .models import Person, PersonList
from .utils import UniqueIdGenerator


def persons_generate(parameters):
    """Generate random persons."""
    fake = Faker(parameters.locale)
    fake.seed_instance(random.randint(0, 1_000_000))
    gen = UniqueIdGenerator("person", _person_id_generator)
    persons = []
    for _ in range(parameters.number):
        f = fake.last_name()
        p = fake.first_name()
        i = gen.next(f, p)
        persons.append(
            Person(
                ident=i,
                family=f,
                personal=p,
            )
        )

    return PersonList(persons=persons)


def _person_id_generator(family, personal):
    """Generate unique ID for a person (CCNNNN)."""
    f = family[0].lower()
    p = personal[0].lower()
    num = random.randint(0, 9999)
    return f"{f}{p}{num:04d}"
