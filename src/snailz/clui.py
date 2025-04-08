"""Command-line interface for snailz."""

import json
from pathlib import Path
import random
import shutil

import click

from .database import database_generate
from .images import images_generate
from .mangle import mangle_assays
from .overall import AllParams, AllData
from . import utils


@click.group()
def cli():
    """Entry point for command-line interface."""


@cli.command()
@click.option("--csvdir", type=click.Path(), help="Path to CSV directory")
@click.option(
    "--params",
    required=True,
    type=click.Path(exists=True),
    help="Path to parameters file",
)
@click.option("--output", type=click.Path(), help="Path to output file")
def data(csvdir, params, output):
    """Generate and save data using provided parameters."""
    try:
        parameters = AllParams.model_validate(json.load(open(params, "r")))
        random.seed(parameters.seed)
        data = AllData.generate(parameters)
        if csvdir is not None:
            csv_dir_path = Path(csvdir)
            _create_csv(csv_dir_path, data)
            database_generate(csv_dir_path, "snailz.db")
            image_dir = csv_dir_path / utils.ASSAYS_DIR
            all_images = images_generate(parameters.assay, data.assays)
            for ident, image in all_images.items():
                image.save(image_dir / f"{ident}.png")
    except OSError as exc:
        utils.fail(str(exc))


@cli.command()
@click.option("--output", type=click.Path(), help="Path to output file")
def params(output):
    """Generate and save parameters."""
    try:
        params = AllParams()
        with open(output, "w") as writer:
            writer.write(utils.json_dump(params))
    except OSError as exc:
        utils.fail(str(exc))


def _create_csv(csv_dir, data):
    """Create CSV files from data."""
    if not csv_dir.is_dir():
        raise ValueError(f"{csv_dir} is not a directory")

    # Machines
    with open(csv_dir / utils.MACHINES_CSV, "w") as writer:
        writer.write(data.machines.to_csv())

    # Assays
    with open(csv_dir / utils.ASSAYS_CSV, "w") as writer:
        writer.write(data.assays.to_csv())
    assays_dir = csv_dir / utils.ASSAYS_DIR
    if assays_dir.is_dir():
        shutil.rmtree(assays_dir)
    assays_dir.mkdir(exist_ok=True)
    for assay in data.assays.items:
        for which in ["readings", "treatments"]:
            with open(assays_dir / f"{assay.ident}_{which}.csv", "w") as writer:
                writer.write(assay.to_csv(which))

    # Mangled assays
    mangle_assays(csv_dir / utils.ASSAYS_DIR, data.persons)

    # Surveys
    surveys_dir = csv_dir / utils.SURVEYS_DIR
    if surveys_dir.is_dir():
        shutil.rmtree(surveys_dir)
    surveys_dir.mkdir(exist_ok=True)
    for survey in data.surveys.items:
        with open(surveys_dir / f"{survey.ident}.csv", "w") as writer:
            writer.write(survey.to_csv())

    # Persons
    with open(csv_dir / utils.PERSONS_CSV, "w") as writer:
        writer.write(data.persons.to_csv())

    # Specimens
    with open(csv_dir / utils.SPECIMENS_CSV, "w") as writer:
        writer.write(data.specimens.to_csv())


if __name__ == "__main__":
    cli()
