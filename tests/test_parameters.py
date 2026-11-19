"""Test parameter object."""

import argparse
from datetime import date
import json
import pytest
from snailz import Parameters
from snailz.main import _initialize


def test_parameters_as_json():
    parameters = Parameters()
    d = json.loads(parameters.as_json())
    assert set(parameters.__dict__.keys()) == set(d.keys())


def test_initialize_date_override():
    args = argparse.Namespace(params=None, override=["start_date=2026-01-15"])
    params = _initialize(args)
    assert params.start_date == date(2026, 1, 15)


def test_initialize_malformed_override_rejected():
    args = argparse.Namespace(params=None, override=["bogus"])
    with pytest.raises(ValueError):
        _initialize(args)
