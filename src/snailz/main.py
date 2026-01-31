"""Synthesize data."""

import argparse
from faker import Faker
import json
from pathlib import Path
import random
import sys
from typing import Any

from .assay import Assay
from .grid import Grid
from .machine import Machine
from .parameters import Parameters
from .person import Person
from .rating import Rating
from .species import Species
from .specimen import Specimen
from ._base_mixin import BaseMixin
from ._utils import UnquotedDatabase


DB_FILE = "snailz.db"


def main():
    """Main command-line driver."""

    args = _parse_args()
    if args.defaults:
        print(Parameters().as_json())
        return 0

    params = _initialize(args)
    data = _synthesize(params)

    _save_params(args.outdir, params)
    classes = (Grid, Machine, Person, Rating, Assay, Species, Specimen)
    _save_csv(args.outdir, classes, data)
    _save_db(args.outdir, classes, data)
    _save_images(args.outdir, data[Grid])

    return 0


def _ensure_dir(dirname: str):
    """
    Ensure directory exists.

    Args:
        dirname: Path to directory.
    """

    dirpath = Path(dirname)
    if not dirpath.is_dir():
        dirpath.mkdir(exist_ok=True)


def _initialize(args: argparse.Namespace) -> Parameters:
    """
    Initialize for data synthesis.

    Args:
        args: Taken from command-line arguments.

    Returns:
        Data synthesis parameters object.
    """

    if args.params:
        with open(args.params, "r") as reader:
            params = Parameters.model_validate(json.load(reader))
    else:
        params = Parameters()

    for ov in args.override:
        fields = ov.split("=")
        assert len(fields) == 2, f"malformed override {ov}"
        key, value = fields
        assert hasattr(params, key), f"unknown override key {key}"
        prior = getattr(params, key)
        setattr(params, key, type(prior)(value))

    random.seed(params.seed)

    return params


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Object holding values from command-line arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--defaults", action="store_true", help="show default parameters"
    )
    parser.add_argument("--outdir", default=None, help="output directory")
    parser.add_argument(
        "--override", default=[], nargs="+", help="name=value parameters"
    )
    parser.add_argument("--params", default=None, help="JSON parameter file")
    return parser.parse_args()


def _save_csv(outdir: Path | str, classes: list[BaseMixin], data: dict[BaseMixin, Any]):
    """
    Save synthesized data as CSV.

    Args:
        outdir: Output directory.
        classes: Ordered list of classes to save.
        data: Class-to-data dictionary of values to save.
    """

    if (outdir is None) or (outdir == "-"):
        return

    _ensure_dir(outdir)
    for cls in classes:
        cls.save_csv(outdir, data[cls])

    for g in data[Grid]:
        with open(Path(outdir, f"{g.ident}.csv"), "w") as writer:
            print(g, file=writer)


def _save_db(outdir: Path | str, classes: list[BaseMixin], data: dict[BaseMixin, Any]):
    """
    Save synthesized data to database.

    Args:
        outdir: Output directory.
        classes: Ordered list of classes to save.
        data: Class-to-data dictionary of values to save.
    """

    if (outdir is None) or (outdir == "-"):
        return

    _ensure_dir(outdir)
    dbpath = Path(outdir, DB_FILE)
    dbpath.unlink(missing_ok=True)

    db = UnquotedDatabase(dbpath)
    for cls in classes:
        cls.save_db(db, data[cls])


def _save_images(outdir: Path | str, grids: list[Grid]):
    """
    Save grids as images.

    Args:
        outdir: Output directory.
        grids: Grids to save.
    """

    scale = max(g.min_max()[1] for g in grids)
    for g in grids:
        g.as_image(scale).save(Path(outdir, f"{g.ident}.png"))


def _save_params(outdir: Path | str, params: Parameters):
    """
    Save parameters as JSON.

    Args:
        outdir: Output directory.
        params: Parameters to save.
    """

    if outdir is None:
        return

    if outdir == "-":
        sys.stdout.write(params.as_json())
    else:
        _ensure_dir(Path(outdir))
        with open(Path(outdir, "params.json"), "w") as writer:
            writer.write(params.as_json())


def _synthesize(params: Parameters) -> dict[BaseMixin, Any]:
    """
    Synthesize data.

    Args:
        params: Data synthesis parameters.

    Returns:
        Dictionary mapping classes to generated data.
    """

    grids = Grid.make(params)
    persons = Person.make(params, Faker(params.locale))
    machines = Machine.make(params)
    ratings = Rating.make(params, persons, machines)
    assays = Assay.make(params, grids, ratings)
    species = Species.make(params)
    specimens = Specimen.make(params, grids, species[0])
    return {
        Assay: assays,
        Grid: grids,
        Person: persons,
        Machine: machines,
        Rating: ratings,
        Species: species,
        Specimen: specimens,
    }


if __name__ == "__main__":
    sys.exit(main())
