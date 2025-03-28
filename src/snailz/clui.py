"""Command-line interface for snailz.

Each subcommand takes options --output (output file path), --params (parameter
file), and --seed (random number seed) along with command-specific parameters.
If a parameter file is given, it is read first and additional parameters
override its values. If a parameter file is not given, all other parameters
are required.
"""

from datetime import date
import json
from pathlib import Path
import random

import click
from pydantic import BaseModel

from .assays import AssayParams, assays_generate, assays_to_csv
from .grid import Grid, GridParams, grid_generate
from .people import AllPersons, PeopleParams, people_generate
from .specimens import (
    AllSpecimens,
    SpecimenParams,
    specimens_generate,
)
from .mangle import mangle_assays
from . import defaults
from . import utils


@click.group()
def cli():
    """Command-line interface for snailz."""


@cli.command()
@click.option(
    "--baseline",
    type=float,
    help="Baseline reading value for non-susceptible specimens (must be > 0)",
)
@click.option("--end-date", callback=utils.validate_date, help="End date (YYYY-MM-DD)")
@click.option(
    "--mutant", type=float, help="Reading value for susceptible specimens (must be > 0)"
)
@click.option("--noise", type=float, help="Noise level for readings (must be > 0)")
@click.option("--output", type=click.Path(), help="Path to JSON output file")
@click.option(
    "--params", type=click.Path(exists=True), help="Path to JSON parameter file"
)
@click.option("--people", type=click.Path(exists=True), help="Path to people JSON file")
@click.option("--plate-size", type=int, help="Size of assay plate (must be > 0)")
@click.option("--seed", type=int, help="Random seed")
@click.option(
    "--specimens", type=click.Path(exists=True), help="Path to specimens JSON file"
)
@click.option(
    "--start-date", callback=utils.validate_date, help="Start date (YYYY-MM-DD)"
)
@click.pass_context
def assays(
    ctx,
    baseline=None,
    end_date=None,
    mutant=None,
    noise=None,
    output=None,
    params=None,
    people=None,
    plate_size=None,
    seed=None,
    specimens=None,
    start_date=None,
):
    """Generate assays for specimens within a date range."""
    try:
        # Load previously-generated data.
        people = utils.load_data("people", people, AllPersons)
        specimens = utils.load_data("specimens", specimens, AllSpecimens)

        # Get parameters for assay generation
        supplied = (
            ("baseline", baseline),
            ("end_date", end_date),
            ("mutant", mutant),
            ("noise", noise),
            ("plate_size", plate_size),
            ("seed", seed),
            ("start_date", start_date),
        )
        parameters = _get_params(
            "assays",
            AssayParams,
            supplied,
            params,
            end_date=date.fromisoformat,
            start_date=date.fromisoformat,
        )
        random.seed(parameters.seed)

        # Generate assays with specimens and people
        result = assays_generate(parameters, specimens, people)
        utils.report_result(output, result)
    except Exception as e:
        utils.fail(f"Error generating assays: {str(e)}")


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Path to input JSON file",
)
@click.option(
    "--kind",
    type=click.Choice(["assays", "grid", "people", "specimens"]),
    required=True,
    help="Type of data to convert",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Path to output CSV file (should be a directory for assays)",
)
def convert(input, kind, output):
    """Convert JSON data to CSV format.

    Converts grid, specimens, or assays data from JSON to CSV format.
    If output is not specified, writes to standard output.
    """
    try:
        # Load the input file based on kind
        if kind == "assays":
            assays_to_csv(input, output)
        elif kind == "grid":
            data = utils.load_data("grid", input, Grid)
            content = data.to_csv()
            _write_content(output, content)
        elif kind == "people":
            data = utils.load_data("people", input, AllPersons)
            content = data.to_csv()
            _write_content(output, content)
        elif kind == "specimens":
            data = utils.load_data("specimens", input, AllSpecimens)
            content = data.to_csv()
            _write_content(output, content)
        else:
            raise ValueError(f"unknown kind {kind}")
    except Exception as e:
        utils.fail(f"Error converting data: {str(e)}")


@cli.command()
@click.option("--depth", type=int, help="Grid depth")
@click.option("--output", type=click.Path(), help="Path to JSON output file")
@click.option(
    "--params", type=click.Path(exists=True), help="Path to JSON parameter file"
)
@click.option("--seed", type=int, help="Random seed")
@click.option("--size", type=int, help="Grid size")
@click.pass_context
def grid(
    ctx,
    depth=None,
    output=None,
    params=None,
    seed=None,
    size=None,
):
    """Generate grid."""
    try:
        supplied = (
            ("depth", depth),
            ("seed", seed),
            ("size", size),
        )
        parameters = _get_params("grid", GridParams, supplied, params)
        random.seed(parameters.seed)
        result = grid_generate(parameters)
        utils.report_result(output, result)
    except Exception as e:
        utils.fail(f"Error generating grid: {str(e)}")


@cli.command()
@click.option(
    "--output",
    type=click.Path(file_okay=False),
    help="Directory to create parameter files in (defaults to current directory)",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing parameter files",
)
def init(output=None, overwrite=False):
    """Initialize parameter files for snailz.

    Creates JSON parameter files in the specified directory (or current directory
    if not specified). Creates the directory if it doesn't exist.

    By default, will not overwrite existing files unless --overwrite is specified.
    """
    try:
        output_dir = Path.cwd() if output is None else Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)
        params = {
            "assays.json": defaults.DEFAULT_ASSAY_PARAMS,
            "grid.json": defaults.DEFAULT_GRID_PARAMS,
            "people.json": defaults.DEFAULT_PEOPLE_PARAMS,
            "specimens.json": defaults.DEFAULT_SPECIMEN_PARAMS,
        }

        if not overwrite:
            _check_not_overwriting(output_dir, params)

        for filename, param_obj in params.items():
            file_path = output_dir / filename
            with file_path.open("w") as writer:
                param_dict = param_obj.model_dump()
                for key, value in param_dict.items():
                    if isinstance(value, date):
                        param_dict[key] = value.isoformat()
                json.dump(param_dict, writer, indent=4)
                writer.write("\n")

    except Exception as e:
        utils.fail(f"Error creating parameter files: {str(e)}")


@cli.command()
@click.option(
    "--dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Directory containing assay CSV files",
)
@click.option(
    "--people",
    type=click.Path(exists=True),
    required=True,
    help="Path to people.csv file",
)
@click.option(
    "--seed", type=int, required=True, help="Random seed for assigning people"
)
def mangle(seed, dir, people):
    """Modify assay files by reassigning people.

    This command takes assay files in a directory and reassigns the people
    who performed the assays using the provided seed for random number generation.
    """
    try:
        random.seed(seed)
        mangle_assays(dir, people)
    except Exception as e:
        utils.fail(f"Error mangling assays: {str(e)}")


@cli.command()
@click.option("--locale", type=str, help="Locale for generating people")
@click.option("--number", type=int, help="Number of people to generate")
@click.option("--output", type=click.Path(), help="Path to JSON output file")
@click.option(
    "--params", type=click.Path(exists=True), help="Path to JSON parameter file"
)
@click.option("--seed", type=int, help="Random seed")
@click.pass_context
def people(
    ctx,
    locale=None,
    number=None,
    output=None,
    params=None,
    seed=None,
):
    """Generate people."""
    try:
        supplied = (
            ("locale", locale),
            ("number", number),
            ("seed", seed),
        )
        parameters = _get_params("people", PeopleParams, supplied, params)
        random.seed(parameters.seed)
        result = people_generate(parameters)
        utils.report_result(output, result)
    except Exception as e:
        utils.fail(f"Error generating people: {str(e)}")


@cli.command()
@click.option("--grid", type=str, help="Path to grid JSON file")
@click.option("--length", type=int, help="Length of each genome")
@click.option("--max-mass", type=float, help="Maximum specimen mass")
@click.option("--min-mass", type=float, help="Minimum specimen mass")
@click.option("--mut-scale", type=float, help="Mutation scaling factor")
@click.option("--mutations", type=int, help="Number of possible mutation loci")
@click.option("--number", type=int, help="Number of specimens to generate")
@click.option("--output", type=click.Path(), help="Path to JSON output file")
@click.option(
    "--params", type=click.Path(exists=True), help="Path to JSON parameter file"
)
@click.option("--seed", type=int, help="Random seed")
@click.pass_context
def specimens(
    ctx,
    grid=None,
    length=None,
    max_mass=None,
    min_mass=None,
    mut_scale=None,
    mutations=None,
    number=None,
    output=None,
    params=None,
    seed=None,
):
    """Generate specimens."""
    try:
        # Load previously-generated data.
        grid = utils.load_data("grid", grid, Grid)

        # Get parameters for specimen generation.
        supplied = (
            ("length", length),
            ("max_mass", max_mass),
            ("min_mass", min_mass),
            ("mut_scale", mut_scale),
            ("mutations", mutations),
            ("number", number),
            ("seed", seed),
        )
        parameters = _get_params("specimens", SpecimenParams, supplied, params)
        random.seed(parameters.seed)
        result = specimens_generate(parameters, grid)
        utils.report_result(output, result)
    except Exception as e:
        utils.fail(f"Error generating specimens: {str(e)}")


def _check_not_overwriting(output_dir: Path, params: dict[str, BaseModel]) -> None:
    existing_files = []
    for filename in params.keys():
        file_path = output_dir / filename
        if file_path.exists():
            existing_files.append(str(file_path))

    if existing_files:
        msg = f"Refusing to overwrite {', '.join(existing_files)}"
        utils.fail(msg)


def _get_params(
    caller: str,
    param_class: BaseModel,
    supplied: tuple[tuple],
    params_file: str | None,
    **converters: dict[str, callable],
) -> BaseModel:
    """Get and check parameter values.

    Parameters:
        caller: Name of the calling function for error messages
        param_class: Pydantic parameter class
        supplied: Tuple of (name, value) pairs for CLI parameters
        params_file: Path to JSON parameter file, or None
        converters: Optional converters for specific parameter values

    Returns:
        An instance of the param_class with validated parameters
    """
    # Read parameter file if given.
    result = {}
    if params_file:
        with open(params_file, "r") as f:
            result = json.load(f)
            for name, conv in converters.items():
                if name in result:
                    result[name] = conv(result[name])

    # Override with extra parameters
    for name, value in supplied:
        if value is not None:
            result[name] = value

    # Create and return parameter object (does validation)
    return param_class(**result)


def _write_content(output: str | None, content: str) -> None:
    """Write content to standard output or a file."""
    if output:
        with open(output, "w") as writer:
            writer.write(content)
    else:
        print(content, end="")


if __name__ == "__main__":
    cli()
