"""Command-line interface for snailz."""

import json

import click

from .models import AllParams
from . import utils


@click.group()
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Entry point for command-line interface."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


@cli.command()
@click.option(
    "--params",
    required=True,
    type=click.Path(exists=True),
    help="Path to parameters file",
)
@click.option(
    "--output", required=True, type=click.Path(), help="Path to output directory"
)
@click.pass_context
def data(ctx, params, output):
    """Process data using parameters file and save to the output directory."""


@cli.command()
@click.option(
    "--output", required=True, type=click.Path(), help="Path to output directory"
)
@click.pass_context
def params(ctx, output):
    """Generate parameters and save to the specified output directory."""
    verbose = ctx.obj["VERBOSE"]
    params = AllParams()
    as_json = json.dumps(params.model_dump(), indent=4)
    try:
        with open(output, "w") as writer:
            writer.write(as_json)
            utils.report(verbose, f"wrote parameter file {output}")
    except OSError as exc:
        utils.fail(str(exc))


if __name__ == "__main__":
    cli(obj={})
