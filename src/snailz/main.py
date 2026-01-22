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
from .persist import objects_to_csv, objects_to_db
from .person import Person
from .rating import Rating
from .sample import Sample
from . import utils


DB_FILE = "snailz.db"


def main():
    """Main command-line driver."""

    args = _parse_args()

    if args.defaults:
        print(utils.json_dump(Parameters()))
        return 0

    params = _initialize(args)
    grids, persons, samples, machines, ratings = _synthesize(params)
    changes = do_all_effects(params, grids, persons, samples)
    _save_csv(args, grids, persons, samples, machines, ratings, changes)
    _save_db(args, grids, persons, samples, machines, ratings)

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


def _save_csv(args, grids, persons, samples, machines, ratings, changes):
    """Save synthesized data as CSV."""

    if not args.outdir:
        return

    elif args.outdir == "-":
        outdir = None

    else:
        outdir = Path(args.outdir)
        if not outdir.is_dir():
            outdir.mkdir(exist_ok=True)

    for g in grids:
        with utils.file_or_std(outdir, f"{g.grid_id}.csv", "w") as writer:
            print(g, file=writer)

    with utils.file_or_std(outdir, "grids.csv", "w") as writer:
        print(Grid.tidy(grids), file=writer)

    for name, cls, data in (
        ("machines", Machine, machines),
        ("persons", Person, persons),
        ("ratings", Rating, ratings),
        ("samples", Sample, samples),
    ):
        with utils.file_or_std(outdir, f"{name}.csv", "w") as writer:
            objects_to_csv(writer, data)

    with utils.file_or_std(outdir, "changes.json", "w") as writer:
        json.dump(changes, writer)


def _save_db(args, grids, persons, samples, machines, ratings):
    """Save synthesized data as CSV."""

    if (not args.outdir) or (args.outdir == "-"):
        return

    outdir = Path(args.outdir)
    if not outdir.is_dir():
        outdir.mkdir(exist_ok=True)
    dbpath = outdir / DB_FILE
    dbpath.unlink(missing_ok=True)

    cnx = sqlite3.connect(dbpath)

    for table, data in (
        ("machine", machines),
        ("person", persons),
        ("rating", ratings),
        ("sample", samples),
    ):
        objects_to_db(cnx, table, data)

    cnx.close()


def _synthesize(params):
    """Synthesize data."""

    grids = Grid.make(params)
    persons = Person.make(params)
    samples = Sample.make(params, grids, persons)
    machines = Machine.make(params)
    ratings = Rating.make(persons, machines)
    return grids, persons, samples, machines, ratings


if __name__ == "__main__":
    sys.exit(main())
