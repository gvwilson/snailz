"""Test entire scenario."""

from pathlib import Path
import random

from snailz.params import AssayParams, ScenarioParams, SpecimenParams
from snailz.scenario import Scenario


def test_scenario_creates_correct_files(fs):
    params = ScenarioParams(
        rng_seed=987654,
        num_sites=1,
        num_specimens=1,
        num_machines=1,
        num_persons=1,
        assays_per_specimen=1,
        specimen_params=SpecimenParams(),
        assay_params=AssayParams(),
    )
    random.seed(params.rng_seed)
    scenario = Scenario.generate(params)

    root = Path("/tmp")
    scenario.to_csv(root)
    for filename in ["assays.csv", "machines.csv", "persons.csv", "specimens.csv"]:
        assert (root / filename).is_file()
    assert len(list(root.glob("**/G*.csv"))) == 1
    assert len(list(root.glob("**/*_raw.csv"))) == 1
    assert len(list(root.glob("**/*_readings.csv"))) == 1
    assert len(list(root.glob("**/*_treatments.csv"))) == 1
    assert len(list(root.glob("*.png"))) == 1
