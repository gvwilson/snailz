"""Test parameter object."""

import json
from snailz import Parameters


def test_parameters_as_json():
    parameters = Parameters()
    d = json.loads(parameters.as_json())
    assert set(parameters.__dict__.keys()) == set(d.keys())
