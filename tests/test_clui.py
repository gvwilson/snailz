"""Test CLI command functionality."""

import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from datetime import date

from snailz.clui import (
    cli,
    assays,
    convert,
    grid,
    init,
    mangle,
    people,
    specimens,
)
from snailz.defaults import (
    DEFAULT_SPECIMEN_PARAMS,
    DEFAULT_PEOPLE_PARAMS,
    DEFAULT_ASSAY_PARAMS,
)
from snailz.grid import Grid, GridParams
from snailz.people import AllPersons
from snailz.specimens import AllSpecimens
from snailz.assays import AllAssays, Assay, ASSAYS_SUBDIR
from snailz.utils import serialize_values


def create_test_assays(fs):
    """Create a test assays data file and return its path."""
    assays_data = AllAssays(
        items=[
            Assay(
                performed=date(2023, 1, 15),
                ident="123456",
                specimen_id="AB1234",
                person_id="jd1234",
                readings=[[1.5, 2.5], [3.5, 4.5]],
                treatments=[["S", "C"], ["C", "S"]],
            )
        ],
        params=DEFAULT_ASSAY_PARAMS,
    )

    assays_file = "/test_assays.json"
    fs.create_file(
        assays_file,
        contents=json.dumps(assays_data.model_dump(), default=serialize_values),
    )
    return assays_file


def create_test_grid(fs):
    """Create a test grid data file and return its path."""
    grid_params = GridParams(depth=3, seed=12345, size=3)
    grid_data = Grid(
        grid=[[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        params=grid_params,
    )

    grid_file = "/test_grid.json"
    fs.create_file(
        grid_file,
        contents=json.dumps(grid_data.model_dump(), default=serialize_values),
    )
    return grid_file


def create_test_people(fs):
    """Create a test people data file and return its path."""
    people_data = AllPersons(
        individuals=[
            {"personal": "John", "family": "Doe", "ident": "jd1234"},
            {"personal": "Jane", "family": "Smith", "ident": "js5678"},
        ],
        params=DEFAULT_PEOPLE_PARAMS,
    )

    people_file = "/test_people.json"
    fs.create_file(
        people_file,
        contents=json.dumps(people_data.model_dump(), default=serialize_values),
    )
    return people_file


def create_test_specimens(fs):
    """Create a test specimens data file and return its path."""
    specimens_data = AllSpecimens(
        individuals=[
            {
                "genome": "ACGT",
                "ident": "AB1234",
                "mass": 1.5,
                "site": {"x": 1, "y": 2},
            }
        ],
        loci=[0, 2],
        reference="ACGT",
        susceptible_base="A",
        susceptible_locus=0,
        params=DEFAULT_SPECIMEN_PARAMS,
    )

    specimens_file = "/test_specimens.json"
    fs.create_file(
        specimens_file,
        contents=json.dumps(specimens_data.model_dump(), default=serialize_values),
    )
    return specimens_file


@pytest.fixture
def runner():
    """Create a CLI runner for testing Click commands."""
    return CliRunner()


# Tests for main CLI command
def test_cli_help(runner):
    """Test the help option of the main CLI command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Command-line interface for snailz" in result.output


# Tests for convert command
def test_convert_grid_stdout(runner, fs):
    """Test converting grid data to CSV and writing to stdout."""
    grid_file = create_test_grid(fs)
    result = runner.invoke(convert, ["--input", grid_file, "--kind", "grid"])
    assert result.exit_code == 0
    assert "0,1,2" in result.output
    assert "3,4,5" in result.output
    assert "6,7,8" in result.output


def test_convert_grid_file(runner, fs):
    """Test converting grid data to CSV and writing to a file."""
    grid_file = create_test_grid(fs)
    output_file = "/output_grid.csv"

    result = runner.invoke(
        convert, ["--input", grid_file, "--kind", "grid", "--output", output_file]
    )

    assert result.exit_code == 0
    assert fs.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert "0,1,2" in content
        assert "3,4,5" in content
        assert "6,7,8" in content


def test_convert_people_stdout(runner, fs):
    """Test converting people data to CSV and writing to stdout."""
    people_file = create_test_people(fs)
    result = runner.invoke(convert, ["--input", people_file, "--kind", "people"])

    assert result.exit_code == 0
    assert "ident,personal,family" in result.output
    assert "jd1234,John,Doe" in result.output
    assert "js5678,Jane,Smith" in result.output


def test_convert_people_file(runner, fs):
    """Test converting people data to CSV and writing to a file."""
    people_file = create_test_people(fs)
    output_file = "/output_people.csv"

    result = runner.invoke(
        convert, ["--input", people_file, "--kind", "people", "--output", output_file]
    )

    assert result.exit_code == 0
    assert fs.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert "ident,personal,family" in content
        assert "jd1234,John,Doe" in content
        assert "js5678,Jane,Smith" in content


def test_convert_assays_stdout(runner, fs):
    """Test converting assays data to CSV and writing to stdout."""
    assays_file = create_test_assays(fs)
    result = runner.invoke(convert, ["--input", assays_file, "--kind", "assays"])

    assert result.exit_code == 0
    assert "ident,specimen_id,performed,performed_by" in result.output
    assert "123456,AB1234,2023-01-15,jd1234" in result.output


def test_convert_assays_directory(runner, fs):
    """Test converting assays data to CSV files in a directory."""
    assays_file = create_test_assays(fs)
    output_dir = "/output_assays"
    fs.create_dir(output_dir)

    result = runner.invoke(
        convert, ["--input", assays_file, "--kind", "assays", "--output", output_dir]
    )

    assert result.exit_code == 0

    # Check summary file
    summary_file = f"{output_dir}/assays.csv"
    assert fs.exists(summary_file)

    with open(summary_file, "r") as f:
        content = f.read()
        assert "ident,specimen_id,performed,performed_by" in content
        assert "123456,AB1234,2023-01-15,jd1234" in content

    # Check assay directory creation
    assays_dir = f"{output_dir}/{ASSAYS_SUBDIR}"
    assert fs.exists(assays_dir)

    # Check individual assay files
    design_file = f"{assays_dir}/123456_design.csv"
    assay_file = f"{assays_dir}/123456_assay.csv"

    assert fs.exists(design_file)
    assert fs.exists(assay_file)

    # Check design file content
    with open(design_file, "r") as f:
        content = f.read()
        assert "id,123456" in content
        assert "specimen,AB1234" in content
        assert "performed,2023-01-15" in content
        assert "performed_by,jd1234" in content
        assert ",A,B" in content
        assert "1,S,C" in content
        assert "2,C,S" in content

    # Check assay file content
    with open(assay_file, "r") as f:
        content = f.read()
        assert "id,123456" in content
        assert "specimen,AB1234" in content
        assert "performed,2023-01-15" in content
        assert "performed_by,jd1234" in content
        assert ",A,B" in content
        assert "1,1.5,2.5" in content
        assert "2,3.5,4.5" in content


def test_convert_specimens_stdout(runner, fs):
    """Test converting specimens data to CSV and writing to stdout."""
    specimens_file = create_test_specimens(fs)
    result = runner.invoke(convert, ["--input", specimens_file, "--kind", "specimens"])

    assert result.exit_code == 0
    assert "ident,x,y,genome,mass" in result.output
    assert "AB1234,1,2,ACGT,1.5" in result.output


def test_convert_invalid_kind(runner, fs):
    """Test convert command with invalid kind parameter."""
    grid_file = create_test_grid(fs)
    result = runner.invoke(convert, ["--input", grid_file, "--kind", "invalid"])

    assert result.exit_code != 0
    # Check for the error message from Click's choice validation
    assert "is not one of" in result.output


def test_convert_nonexistent_file(runner):
    """Test convert command with a nonexistent input file."""
    result = runner.invoke(convert, ["--input", "/nonexistent.json", "--kind", "grid"])

    assert result.exit_code != 0
    assert "Error" in result.output


# Tests for grid command
def test_grid_command_with_params(runner):
    """Test grid command with parameters."""
    result = runner.invoke(grid, ["--size", "3", "--depth", "3", "--seed", "12345"])

    assert result.exit_code == 0
    # The output should be JSON
    assert "grid" in result.output
    assert "params" in result.output


def test_grid_command_with_params_file(runner, fs):
    """Test grid command with parameters file."""
    # Create a params file
    params_file = "/grid_params.json"
    params = {"size": 4, "depth": 5, "seed": 67890}
    fs.create_file(params_file, contents=json.dumps(params))

    result = runner.invoke(grid, ["--params", params_file])

    assert result.exit_code == 0
    assert "grid" in result.output
    assert "params" in result.output

    # Ensure the parameters from the file were used
    assert '"seed": 67890' in result.output
    assert '"size": 4' in result.output
    assert '"depth": 5' in result.output


def test_grid_command_with_output_file(runner, fs):
    """Test grid command with output to file."""
    output_file = "/output_grid.json"

    result = runner.invoke(
        grid,
        ["--size", "3", "--depth", "3", "--seed", "12345", "--output", output_file],
    )

    assert result.exit_code == 0
    assert fs.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert "grid" in content
        assert "params" in content


# Tests for people command
def test_people_command_with_params(runner):
    """Test people command with parameters."""
    result = runner.invoke(
        people, ["--locale", "en_US", "--number", "2", "--seed", "12345"]
    )

    assert result.exit_code == 0
    assert "individuals" in result.output
    assert "params" in result.output


def test_people_command_with_params_file(runner, fs):
    """Test people command with parameters file."""
    # Create a params file
    params_file = "/people_params.json"
    params = {"locale": "en_US", "number": 3, "seed": 67890}
    fs.create_file(params_file, contents=json.dumps(params))

    result = runner.invoke(people, ["--params", params_file])

    assert result.exit_code == 0
    assert "individuals" in result.output
    assert "params" in result.output

    # Ensure the parameters from the file were used
    assert '"seed": 67890' in result.output
    assert '"number": 3' in result.output


def test_people_command_with_output_file(runner, fs):
    """Test people command with output to file."""
    output_file = "/output_people.json"

    result = runner.invoke(
        people,
        [
            "--locale",
            "en_US",
            "--number",
            "2",
            "--seed",
            "12345",
            "--output",
            output_file,
        ],
    )

    assert result.exit_code == 0
    assert fs.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert "individuals" in content
        assert "params" in content


# Tests for specimens command
def test_specimens_command_with_params(runner, fs):
    """Test specimens command with parameters and grid file."""
    grid_file = create_test_grid(fs)

    result = runner.invoke(
        specimens,
        [
            "--grid",
            grid_file,
            "--length",
            "10",
            "--max-mass",
            "5.0",
            "--min-mass",
            "1.0",
            "--mut-scale",
            "0.5",
            "--mutations",
            "3",
            "--number",
            "2",
            "--seed",
            "12345",
        ],
    )

    assert result.exit_code == 0
    assert "individuals" in result.output
    assert "params" in result.output
    assert "loci" in result.output
    assert "reference" in result.output


def test_specimens_command_with_params_file(runner, fs):
    """Test specimens command with parameters file and grid file."""
    grid_file = create_test_grid(fs)

    # Create a params file
    params_file = "/specimens_params.json"
    params = {
        "length": 8,
        "max_mass": 4.0,
        "min_mass": 1.0,
        "mut_scale": 0.3,
        "mutations": 2,
        "number": 3,
        "seed": 67890,
    }
    fs.create_file(params_file, contents=json.dumps(params))

    result = runner.invoke(specimens, ["--grid", grid_file, "--params", params_file])

    assert result.exit_code == 0
    assert "individuals" in result.output
    assert "params" in result.output

    # Ensure the parameters from the file were used
    assert '"seed": 67890' in result.output
    assert '"length": 8' in result.output


def test_specimens_command_with_output_file(runner, fs):
    """Test specimens command with output to file."""
    grid_file = create_test_grid(fs)
    output_file = "/output_specimens.json"

    result = runner.invoke(
        specimens,
        [
            "--grid",
            grid_file,
            "--length",
            "10",
            "--max-mass",
            "5.0",
            "--min-mass",
            "1.0",
            "--mut-scale",
            "0.5",
            "--mutations",
            "3",
            "--number",
            "2",
            "--seed",
            "12345",
            "--output",
            output_file,
        ],
    )

    assert result.exit_code == 0
    assert fs.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert "individuals" in content
        assert "params" in content


# Tests for assays command
def test_assays_command_with_params(runner, fs):
    """Test assays command with parameters and required files."""
    people_file = create_test_people(fs)
    specimens_file = create_test_specimens(fs)

    result = runner.invoke(
        assays,
        [
            "--people",
            people_file,
            "--specimens",
            specimens_file,
            "--baseline",
            "1.0",
            "--end-date",
            "2023-02-28",
            "--mutant",
            "10.0",
            "--noise",
            "0.5",
            "--plate-size",
            "3",
            "--seed",
            "12345",
            "--start-date",
            "2023-01-01",
        ],
    )

    assert result.exit_code == 0
    assert "items" in result.output
    assert "params" in result.output


def test_assays_command_with_params_file(runner, fs):
    """Test assays command with parameters file and required files."""
    people_file = create_test_people(fs)
    specimens_file = create_test_specimens(fs)

    # Create a params file
    params_file = "/assays_params.json"
    params = {
        "baseline": 2.0,
        "end_date": "2023-03-31",
        "mutant": 15.0,
        "noise": 0.3,
        "plate_size": 4,
        "seed": 67890,
        "start_date": "2023-02-01",
    }
    fs.create_file(params_file, contents=json.dumps(params))

    result = runner.invoke(
        assays,
        [
            "--people",
            people_file,
            "--specimens",
            specimens_file,
            "--params",
            params_file,
        ],
    )

    assert result.exit_code == 0
    assert "items" in result.output
    assert "params" in result.output

    # Ensure the parameters from the file were used
    assert '"seed": 67890' in result.output
    assert '"plate_size": 4' in result.output


def test_assays_command_with_output_file(runner, fs):
    """Test assays command with output to file."""
    people_file = create_test_people(fs)
    specimens_file = create_test_specimens(fs)
    output_file = "/output_assays.json"

    result = runner.invoke(
        assays,
        [
            "--people",
            people_file,
            "--specimens",
            specimens_file,
            "--baseline",
            "1.0",
            "--end-date",
            "2023-02-28",
            "--mutant",
            "10.0",
            "--noise",
            "0.5",
            "--plate-size",
            "3",
            "--seed",
            "12345",
            "--start-date",
            "2023-01-01",
            "--output",
            output_file,
        ],
    )

    assert result.exit_code == 0
    assert fs.exists(output_file)

    with open(output_file, "r") as f:
        content = f.read()
        assert "items" in content
        assert "params" in content


# Tests for error handling
def test_grid_command_error(runner):
    """Test grid command with invalid parameters triggers error handling."""
    # Missing required parameters should trigger the try/except block
    result = runner.invoke(grid, [])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_people_command_error(runner):
    """Test people command with invalid parameters triggers error handling."""
    # Missing required parameters should trigger the try/except block
    result = runner.invoke(people, [])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_specimens_command_error(runner):
    """Test specimens command with invalid parameters triggers error handling."""
    # Missing required parameters should trigger the try/except block
    result = runner.invoke(specimens, [])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_assays_command_error(runner):
    """Test assays command with invalid parameters triggers error handling."""
    # Missing required parameters should trigger the try/except block
    result = runner.invoke(assays, [])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_mangle_command_error(runner):
    """Test mangle command with invalid parameters triggers error handling."""
    # Missing required parameters should trigger the try/except block
    result = runner.invoke(mangle, [])
    assert result.exit_code != 0
    assert "Error" in result.output


# Test for mangle command
def test_mangle_command(runner, fs):
    """Test mangle command with required files."""
    # Create a directory with assay files
    assays_dir = "/test_assays_dir"
    fs.create_dir(assays_dir)

    # Create a sample assay file
    assay_file = f"{assays_dir}/123456_assay.csv"
    fs.create_file(
        assay_file,
        contents=(
            "id,123456\n"
            "specimen,AB1234\n"
            "performed,2023-01-15\n"
            "performed_by,jd1234\n"
            ",A,B\n"
            "1,1.5,2.5\n"
            "2,3.5,4.5\n"
        ),
    )

    # Create a people JSON file (mangle expects JSON, not CSV)
    people_data = {
        "individuals": [
            {"personal": "John", "family": "Doe", "ident": "jd1234"},
            {"personal": "Jane", "family": "Smith", "ident": "js5678"},
        ]
    }
    people_json = "/people.json"
    fs.create_file(people_json, contents=json.dumps(people_data))

    result = runner.invoke(
        mangle, ["--dir", assays_dir, "--people", people_json, "--seed", "12345"]
    )

    assert result.exit_code == 0

    # Check that raw file was created
    raw_file = f"{assays_dir}/123456_raw.csv"
    assert fs.exists(raw_file)

    # Check raw file has been mangled
    with open(raw_file, "r") as f:
        content = f.read()
        assert "123456" in content  # ID should still be present


# Tests for init command
def test_init_command_default_directory(runner, fs):
    """Test init command with default output directory."""
    # Store the current working directory that will be used
    cwd = fs.cwd

    # Run the init command
    result = runner.invoke(init)

    assert result.exit_code == 0

    # Check all parameter files were created in the current directory
    expected_files = ["assays.json", "grid.json", "people.json", "specimens.json"]
    for filename in expected_files:
        filepath = Path(cwd) / filename
        assert fs.exists(filepath)

        # Check content is valid JSON and has trailing newline
        with open(filepath, "r") as f:
            content_text = f.read()
            assert content_text.endswith("\n"), (
                f"File {filepath} does not end with newline"
            )

            # Reset file pointer and load as JSON
            f.seek(0)
            content = json.load(f)
            assert isinstance(content, dict)
            assert "seed" in content  # All parameter files have seed

            # Check specific fields for each file type
            if filename == "assays.json":
                assert "baseline" in content
                assert "end_date" in content
            elif filename == "grid.json":
                assert "depth" in content
                assert "size" in content
            elif filename == "people.json":
                assert "locale" in content
                assert "number" in content
            elif filename == "specimens.json":
                assert "length" in content
                assert "mutations" in content


def test_init_command_custom_directory(runner, fs):
    """Test init command with custom output directory."""
    # Define a custom directory that doesn't exist yet
    custom_dir = "/custom/params/dir"

    # Run the init command with custom directory
    result = runner.invoke(init, ["--output", custom_dir])

    assert result.exit_code == 0

    # Check the directory was created
    assert fs.exists(custom_dir)

    # Check all parameter files were created in the custom directory
    expected_files = ["assays.json", "grid.json", "people.json", "specimens.json"]
    for filename in expected_files:
        filepath = Path(custom_dir) / filename
        assert fs.exists(filepath)

        # Check content is valid JSON and has trailing newline
        with open(filepath, "r") as f:
            content_text = f.read()
            assert content_text.endswith("\n"), (
                f"File {filepath} does not end with newline"
            )

            # Reset file pointer and load as JSON
            f.seek(0)
            content = json.load(f)
            assert isinstance(content, dict)


def test_init_command_no_overwrite(runner, fs):
    """Test init command respects the overwrite flag."""
    # Create a file that would be overwritten
    cwd = fs.cwd
    existing_file = Path(cwd) / "assays.json"
    fs.create_file(existing_file, contents="{}")

    # Run the init command without overwrite flag
    result = runner.invoke(init)

    # Should fail with error message
    assert result.exit_code != 0
    assert "Refusing" in result.output

    # Original file should be unchanged
    with open(existing_file, "r") as f:
        assert f.read() == "{}"


def test_init_command_with_overwrite(runner, fs):
    """Test init command with overwrite flag."""
    # Create a file that would be overwritten
    cwd = fs.cwd
    existing_file = Path(cwd) / "assays.json"
    fs.create_file(existing_file, contents="{}")

    # Run the init command with overwrite flag
    result = runner.invoke(init, ["--overwrite"])

    # Should succeed
    assert result.exit_code == 0

    # File should be overwritten
    with open(existing_file, "r") as f:
        content = f.read()
        assert content != "{}"
        assert "baseline" in content
