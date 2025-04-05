"""Save data in SQLite database."""

import csv
import sqlite3
from pathlib import Path

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
    for filepath, header, create, insert in (
        (root / utils.ASSAYS_CSV, ASSAYS_HEADER, ASSAYS_CREATE, ASSAYS_INSERT),
        (root / utils.PERSONS_CSV, PERSONS_HEADER, PERSONS_CREATE, PERSONS_INSERT),
        (root / utils.SPECIMENS_CSV, SPECIMENS_HEADER, SPECIMENS_CREATE, SPECIMENS_INSERT),
    ):
        with open(filepath, "r") as stream:
            data = [row for row in csv.reader(stream)]
            assert data[0] == header
            cursor.execute(create)
            cursor.executemany(insert, data[1:])

    conn.commit()

    if db_file is None:
        return conn
    else:
        conn.close()
        return None
