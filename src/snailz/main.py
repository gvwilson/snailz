"""Synthesize data."""

import argparse
import json
from pathlib import Path
import random
import sqlite3
import sys

from .effect import do_all_effects
from .grid import Grid
from .machine import Machine
from .parameters import Parameters
from .person import Person
from .rating import Rating
from .sample import Sample
from . import persist
from . import utils


DB_FILE = "snailz.db"


def main():
    """Main command-line driver."""

    args = _parse_args()
    if args.defaults:
        print(utils.json_dump(Parameters()))
        return 0

    params = _initialize(args)
    data = _synthesize(params)
    data["changes"] = do_all_effects(params, data)

    data["tidy_grids"] = Grid.tidy(params, data["grids"])
    _save_csv(args, data)
    _save_db(args, data)
    _save_params(args, params)

    return 0


def _initialize(args):
    """Initialize for data synthesis."""

    if args.params:
        with open(args.params, "r") as reader:
            params = Parameters.model_validate(json.load(reader))
    else:
        params = Parameters()

    random.seed(params.seed)

    return params


def _parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--defaults", action="store_true", help="show default parameters"
    )
    parser.add_argument("--outdir", default=None, help="output directory")
    parser.add_argument("--params", default=None, help="JSON parameter file")
    return parser.parse_args()


def _save_csv(args, data):
    """Save synthesized data as CSV."""

    if not args.outdir:
        return

    elif args.outdir == "-":
        outdir = None

    else:
        outdir = Path(args.outdir)
        if not outdir.is_dir():
            outdir.mkdir(exist_ok=True)

    persist.grids_to_csv(outdir, data["grids"], data["tidy_grids"])
    for name, cls in (
        ("machines", Machine),
        ("persons", Person),
        ("ratings", Rating),
        ("samples", Sample),
    ):
        with utils.file_or_std(outdir, f"{name}.csv", "w") as writer:
            persist.objects_to_csv(writer, data[name])

    with utils.file_or_std(outdir, "changes.json", "w") as writer:
        json.dump(data["changes"], writer)


def _save_db(args, data):
    """Save synthesized data as CSV."""

    if (not args.outdir) or (args.outdir == "-"):
        return

    outdir = Path(args.outdir)
    if not outdir.is_dir():
        outdir.mkdir(exist_ok=True)
    dbpath = outdir / DB_FILE
    dbpath.unlink(missing_ok=True)

    cnx = sqlite3.connect(dbpath)

    for table, name in (
        ("machine", "machines"),
        ("person", "persons"),
        ("rating", "ratings"),
        ("sample", "samples"),
    ):
        persist.objects_to_db(cnx, table, data[name])

    persist.grids_to_db(cnx, data["tidy_grids"])

    cnx.close()


def _save_params(args, params):
    """Save parameters."""
    if (args.outdir is None) or (args.outdir == "-"):
        return

    with open(Path(args.outdir, "params.json"), "w") as writer:
        writer.write(utils.json_dump(Parameters()))


def _synthesize(params):
    """Synthesize data."""

    grids = Grid.make(params)
    persons = Person.make(params)
    samples = Sample.make(params, grids, persons)
    machines = Machine.make(params)
    ratings = Rating.make(persons, machines)
    return {
        "grids": grids,
        "persons": persons,
        "samples": samples,
        "machines": machines,
        "ratings": ratings,
    }


if __name__ == "__main__":
    sys.exit(main())
