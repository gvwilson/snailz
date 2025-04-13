"""Command-line interface for snailz."""

import json
from pathlib import Path
import random
import zipfile

import click

from .database import database_generate
from .scenario import ScenarioParams, ScenarioData
from . import utils


@click.group()
def cli():
    """Entry point for command-line interface."""


@cli.command()
@click.option("--data", type=click.Path(), help="Path to data directory")
def db(data):
    """Create SQLite database of generated data."""
    try:
        database_generate(Path(data), "snailz.db")
    except Exception as exc:
        utils.fail(str(exc))


@cli.command()
@click.option("--full", is_flag=True, default=False, help="Full details")
@click.option(
    "--params",
    required=True,
    type=click.Path(exists=True),
    help="Path to parameters file",
)
@click.option("--output", type=click.Path(), help="Path to output directory")
@click.option("--seed", default=None, help="Override seed for ad hoc testing")
def data(full, params, output, seed):
    """Generate and save data using provided parameters."""
    try:
        parameters = ScenarioParams.model_validate(json.load(open(params, "r")))
        random.seed(parameters.seed if seed is None else seed)
        data = ScenarioData.generate(parameters)
        ScenarioData.save(Path(output), data, full=full)
    except OSError as exc:
        utils.fail(str(exc))


@cli.command()
@click.option("--output", type=click.Path(), help="Path to output file")
def params(output):
    """Generate and save parameters."""
    try:
        params = ScenarioParams()
        with open(output, "w") as writer:
            writer.write(utils.json_dump(params))
    except OSError as exc:
        utils.fail(str(exc))


@cli.command()
@click.option("--data", type=click.Path(), help="Path to data directory")
@click.option("--output", type=click.Path(), help="Path to output ZIP file")
def zip(data, output):
    """Create ZIP archive of generated data."""
    try:
        _zip_generate(Path(data), Path(output))
    except Exception as exc:
        utils.fail(str(exc))


def _zip_generate(data_dir: Path, output_file: Path) -> None:
    """Create ZIP file of generated data.

    Parameters:
        data_dir: directory containing generated files
        output_file: ZIP file to create
    """
    sources = []
    for pattern in ["**/*.csv", "**/*.png"]:
        sources.extend(data_dir.glob(pattern))
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipper:
        for src in sources:
            zipper.write(src, src.relative_to(data_dir))


if __name__ == "__main__":
    cli()
