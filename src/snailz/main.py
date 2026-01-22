"""Synthesize data."""

import argparse
import csv
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
from . import utils


CREATE_GRID = """\
create table grid (
    grid_id text not null,
    x integer not null,
    y integer not null,
    pollution integer not null
);
"""
INSERT_GRID = """\
insert into grid values (?, ?, ?, ?);
"""

CREATE_PERSON = """\
create table person (
    person_id text not null primary key,
    personal text not null,
    family text not null
);
"""
INSERT_PERSON = """\
insert into person values (?, ?, ?);
"""

CREATE_RATING = """\
create table rating (
    person_id text not null,
    machine_id text not null,
    rating integer
);
"""
INSERT_RATING = """\
insert into rating values(?, ?, ?);
"""

CREATE_SAMPLE = """\
create table sample (
    sample_id text not null primary key,
    grid_id text not null,
    lat real not null,
    lon real not null,
    pollution integer not null,
    person text not null,
    timestamp date,
    mass real
);
"""
INSERT_SAMPLE = """\
insert into sample values (?, ?, ?, ?, ?, ?, ?, ?);
"""


def main():
    """Main command-line driver."""

    args = _parse_args()

    if args.defaults:
        print(utils.json_dump(Parameters()))
        return 0

    params = _initialize(args)
    grids, persons, samples, machines, ratings = _synthesize(params)
    changes = do_all_effects(params, grids, persons, samples)
    _save(args, grids, persons, samples, machines, ratings, changes)
    _save_db(args)

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


def _save(args, grids, persons, samples, machines, ratings, changes):
    """Save synthesized data."""

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
            utils.model_to_csv(writer, data)

    with utils.file_or_std(outdir, "changes.json", "w") as writer:
        json.dump(changes, writer)


def _save_db(args):
    """Convert saved data to SQLite database."""

    if (args.outdir is None) or (args.outdir == "-"):
        return

    db_path = Path(args.outdir, "snailz.db")
    db_path.unlink(missing_ok=True)
    cnx = sqlite3.connect(db_path)
    cur = cnx.cursor()
    for name, create, insert in (
        ("grids", CREATE_GRID, INSERT_GRID),
        ("persons", CREATE_PERSON, INSERT_PERSON),
        ("ratings", CREATE_RATING, INSERT_RATING),
        ("samples", CREATE_SAMPLE, INSERT_SAMPLE),
    ):
        with open(Path(args.outdir, f"{name}.csv"), "r") as reader:
            rows = [r for r in csv.reader(reader)]
            cur.execute(create)
            cur.executemany(insert, rows[1:])
    cnx.commit()
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
