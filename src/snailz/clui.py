"""Command-line interface for snailz."""

import json
import random

import click

from .grids import grids_generate
from .models import AllData, AllParams
from .persons import persons_generate
from .utils import display, fail, report


@click.group()
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Entry point for command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option(
    "--params",
    required=True,
    type=click.Path(exists=True),
    help="Path to parameters file",
)
@click.option("--output", type=click.Path(), help="Path to output file")
@click.pass_context
def data(ctx, params, output):
    """Generate and save data using provided parameters."""
    verbose = ctx.obj["verbose"]
    try:
        with open(params, "r") as reader:
            parameters = AllParams.model_validate(json.load(reader))
            random.seed(parameters.seed)
            grids = grids_generate(parameters.grid)
            persons = persons_generate(parameters.person)
            data = AllData(
                params=parameters,
                grids=grids,
                persons=persons,
            )
            display(output, str(data))
            report(verbose, f"wrote data file {output}")
    except OSError as exc:
        fail(str(exc))


@cli.command()
@click.option(
    "--output", required=True, type=click.Path(), help="Path to output file"
)
@click.pass_context
def params(ctx, output):
    """Generate parameters and save to the specified output directory."""
    verbose = ctx.obj["verbose"]
    params = AllParams()
    as_json = json.dumps(params.model_dump(), indent=4)
    try:
        with open(output, "w") as writer:
            writer.write(as_json)
            report(verbose, f"wrote parameter file {output}")
    except OSError as exc:
        fail(str(exc))


if __name__ == "__main__":
    cli(obj={})
