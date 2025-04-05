"""Save data in SQLite database."""

import csv
import sqlite3
from pathlib import Path

from typing import Callable

from . import utils


ASSAYS_CREATE = """
create table assays (
    ident text primary key,
    specimen text not null,
    person text not null,
    performed text
)
"""
ASSAYS_HEADER = ["ident", "specimen", "person", "performed"]
ASSAYS_INSERT = f"insert into assays values ({', '.join('?' * len(ASSAYS_HEADER))})"

PERSONS_CREATE = """
create table persons (
    ident text primary key,
    personal text not null,
    family text not null
)
"""
PERSONS_HEADER = ["ident", "personal", "family"]
PERSONS_INSERT = f"insert into persons values ({', '.join('?' * len(PERSONS_HEADER))})"

READINGS_CREATE = """
create table readings (
    ident text not null,
    row integer not null,
    col text not null,
    reading text not null
)
"""
READINGS_HEADER = ["ident", "row", "col", "reading"]
READINGS_INSERT = (
    f"insert into readings values ({', '.join('?' * len(READINGS_HEADER))})"
)

SPECIMENS_CREATE = """
create table specimens (
    ident text primary key,
    survey text not null,
    x integer real not null,
    y integer real not null,
    collected text not null,
    genome text not null,
    mass real not null
)
"""
SPECIMENS_HEADER = ["ident", "survey", "x", "y", "collected", "genome", "mass"]
SPECIMENS_INSERT = (
    f"insert into specimens values ({', '.join('?' * len(SPECIMENS_HEADER))})"
)

TREATMENTS_CREATE = """
create table treatments (
    ident text not null,
    row integer not null,
    col text not null,
    treatment text not null
)
"""
TREATMENTS_HEADER = ["ident", "row", "col", "treatment"]
TREATMENTS_INSERT = (
    f"insert into treatments values ({', '.join('?' * len(TREATMENTS_HEADER))})"
)


def database_generate(root: Path, db_file: str | None) -> sqlite3.Connection | None:
    """Create a SQLite database from CSV files.

    Parameters:
        root: Path to directory containing CSV files.
        db_file: Filename for database file or None.

    Returns:
        sqlite3.Connection: Database connection if database is in-memory or None otherwise
    """
    if db_file is None:
        conn = sqlite3.connect(":memory:")
    else:
        db_path = root / db_file
        Path(db_path).unlink(missing_ok=True)
        conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    _import_single_files(root, cursor)
    _import_assay_files(
        root,
        cursor,
        "*_treatments.csv",
        TREATMENTS_CREATE,
        TREATMENTS_INSERT,
        lambda v: v,
    )
    _import_assay_files(
        root,
        cursor,
        "*_readings.csv",
        READINGS_CREATE,
        READINGS_INSERT,
        lambda v: float(v),
    )

    conn.commit()

    if db_file is None:
        return conn
    else:
        conn.close()
        return None


def _import_assay_files(
    root: Path,
    cursor: sqlite3.Cursor,
    pattern: str,
    create: str,
    insert: str,
    convert: Callable,
) -> None:
    """Import data from all clean assay files."""
    cursor.execute(create)
    for filename in (root / utils.ASSAYS_DIR).glob(pattern):
        with open(filename, "r") as stream:
            rows = [r for r in csv.reader(stream)]
            assert rows[0][0] == "id"
            ident = rows[0][1]
            data = [r[1:] for r in rows[5:]]
            temp = []
            for i, row in enumerate(data):
                for j, val in enumerate(row):
                    temp.append((ident, i + 1, chr(ord("A") + j), convert(val)))
            cursor.executemany(insert, temp)


def _import_single_files(root: Path, cursor: sqlite3.Cursor) -> None:
    """Import single CSV files into database."""
    for filepath, header, create, insert in (
        (root / utils.ASSAYS_CSV, ASSAYS_HEADER, ASSAYS_CREATE, ASSAYS_INSERT),
        (root / utils.PERSONS_CSV, PERSONS_HEADER, PERSONS_CREATE, PERSONS_INSERT),
        (
            root / utils.SPECIMENS_CSV,
            SPECIMENS_HEADER,
            SPECIMENS_CREATE,
            SPECIMENS_INSERT,
        ),
    ):
        with open(filepath, "r") as stream:
            data = [row for row in csv.reader(stream)]
            assert data[0] == header
            cursor.execute(create)
            cursor.executemany(insert, data[1:])
