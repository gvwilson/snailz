"""Command-line interface for snailz."""

from datetime import date
import json
from pathlib import Path
import random

import click
from pydantic import BaseModel

from .grids import grids_generate
from .overall import AllData, AllParams
from .persons import persons_generate
from .specimens import specimens_generate
from .utils import display, fail, report


@click.group()
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Entry point for command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--csvdir", type=click.Path(), help="Path to CSV directory")
@click.option(
    "--params",
    required=True,
    type=click.Path(exists=True),
    help="Path to parameters file",
)
@click.option("--output", type=click.Path(), help="Path to output file")
@click.pass_context
def data(ctx, csvdir, params, output):
    """Generate and save data using provided parameters."""
    verbose = ctx.obj["verbose"]
    try:
        with open(params, "r") as reader:
            parameters = AllParams.model_validate(json.load(reader))
            random.seed(parameters.seed)
            grids = grids_generate(parameters.grid)
            persons = persons_generate(parameters.person)
            specimens = specimens_generate(parameters.specimen, "G000", 5)  # FIXME
            data = AllData(
                params=parameters,
                grids=grids,
                persons=persons,
                specimens=specimens,
            )
            display(output, str(data))
            report(verbose, f"wrote data file {output}")
            if csvdir is not None:
                _create_csv(Path(csvdir), data)
                report(verbose, f"wrote CSV to {output}")
    except OSError as exc:
        fail(str(exc))


@cli.command()
@click.option("--output", required=True, type=click.Path(), help="Path to output file")
@click.pass_context
def params(ctx, output):
    """Generate parameters and save to the specified output directory."""
    verbose = ctx.obj["verbose"]
    params = AllParams()
    as_json = json.dumps(params.model_dump(), indent=4, default=_serialize_json)
    try:
        with open(output, "w") as writer:
            writer.write(as_json)
            report(verbose, f"wrote parameter file {output}")
    except OSError as exc:
        fail(str(exc))


def _create_csv(csv_dir, data):
    """Create CSV files from data."""
    if not csv_dir.is_dir():
        raise ValueError(f"{csv_dir} is not a directory")

    with open(csv_dir / "people.csv", "w") as writer:
        writer.write(data.persons.to_csv())

    grids_dir = csv_dir / "grids"
    grids_dir.mkdir(exist_ok=True)
    for grid in data.grids.grids:
        with open(grids_dir / f"{grid.ident}.csv", "w") as writer:
            writer.write(grid.to_csv())


def _serialize_json(obj: object) -> str | dict:
    """Custom JSON serializer for JSON conversion.

    Parameters:
        obj: The object to serialize

    Returns:
        String representation of date objects or dict for Pydantic models

    Raises:
        TypeError: If the object type is not supported for serialization
    """
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise TypeError(f"Type {type(obj)} not serializable")


if __name__ == "__main__":
    cli(obj={})
