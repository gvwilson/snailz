"""Test utilities."""

from faker import Faker
import pytest
import random


@pytest.fixture
def seeded_rng():
    random.seed(12345)
    yield
    random.seed()


@pytest.fixture
def fake(seeded_rng):
    f = Faker()
    f.seed_instance(random.randint(0, 1_000_000))
    return f
