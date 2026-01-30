"""Synthesize data."""

import argparse
from faker import Faker
import json
from pathlib import Path
import random
from sqlite_utils import Database
import sys

from .grid import Grid
from .machine import Machine
from .parameters import Parameters
from .person import Person
from .rating import Rating
from .species import Species
from .specimen import Specimen


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
    _save_db(args.outdir, data)

    return 0


def _ensure_dir(dirname):
    """Ensure directory exists."""

    dirpath = Path(dirname)
    if not dirpath.is_dir():
        dirpath.mkdir(exist_ok=True)


def _initialize(args):
    """Initialize for data synthesis."""

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


def _parse_args():
    """Parse command-line arguments."""

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


def _save_db(outdir, data):
    """Save synthesized data as CSV."""

    if (outdir is None) or (outdir == "-"):
        return

    _ensure_dir(outdir)
    dbpath = Path(outdir, DB_FILE)
    dbpath.unlink(missing_ok=True)

    db = Database(dbpath)
    for cls in (Grid, Machine, Person, Rating, Species, Specimen):
        cls.save_db(db, data[cls.table_name])


def _save_params(outdir, params):
    """Save parameters."""

    if outdir is None:
        return

    if outdir == "-":
        sys.stdout.write(params.as_json())
    else:
        _ensure_dir(Path(outdir))
        with open(Path(outdir, "params.json"), "w") as writer:
            writer.write(params.as_json())


def _synthesize(params):
    """Synthesize data."""

    grids = Grid.make(params)
    persons = Person.make(params, Faker(params.locale))
    machines = Machine.make(params)
    ratings = Rating.make(persons, machines)
    species = Species.make(params)
    specimens = Specimen.make(params, grids, species)
    return {
        Grid.table_name: grids,
        Person.table_name: persons,
        Machine.table_name: machines,
        Rating.table_name: ratings,
        Species.table_name: species,
        Specimen.table_name: specimens,
    }


if __name__ == "__main__":
    sys.exit(main())
