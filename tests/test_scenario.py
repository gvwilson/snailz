"""Test overall scenario."""

from pathlib import Path

import pytest

from snailz.scenario import ScenarioParams, ScenarioData


def test_scenario_saves_all_files(fs):
    params = ScenarioParams()
    data = ScenarioData.generate(params)
    root = Path("/")
    ScenarioData.save(root, data)


def test_scenario_fails_for_nonexist_directory(fs):
    params = ScenarioParams()
    data = ScenarioData.generate(params, with_images=False)
    with pytest.raises(ValueError):
        ScenarioData.save(Path("/nonexist"), data)


def test_scenario_clean_existing_directory(fs):
    params = ScenarioParams()
    root = Path("/")
    temp = root / "assays" / "temp.txt"
    fs.create_file(str(temp), contents="temporary")
    data = ScenarioData.generate(params, with_images=False)
    ScenarioData.save(root, data)
    assert not temp.exists()
