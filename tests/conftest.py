"""Test fixtures and configuration."""

import pytest
from snailz.parameters import Parameters
from snailz.person import Person
from snailz.grid import Grid
from snailz.sample import Sample


@pytest.fixture
def default_params():
    """Default parameters for testing."""

    return Parameters()


@pytest.fixture
def fx_persons(default_params):
    """Sample persons for testing."""

    default_params.num_persons = 3
    return Person.make(default_params)


@pytest.fixture
def fx_grids(default_params):
    """Sample grids for testing."""

    default_params.num_grids = 2
    return Grid.make(default_params)


@pytest.fixture
def fx_samples(default_params, fx_grids, fx_persons):
    """Sample samples for testing."""

    default_params.num_samples = 5
    return Sample.make(default_params, fx_grids, fx_persons)
