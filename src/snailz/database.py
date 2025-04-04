"""Save data in SQLite database."""

import csv
import sqlite3
from pathlib import Path


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
    grid text not null,
    x integer real not null,
    y integer real not null,
    collected text not null,
    genome text not null,
    mass real not null
)
"""
SPECIMENS_HEADER = ["ident", "grid", "x", "y", "collected", "genome", "mass"]
SPECIMENS_INSERT = (
    f"insert into specimens values ({', '.join('?' * len(SPECIMENS_HEADER))})"
)


def database_generate(
    assays: Path | str,
    persons: Path | str,
    specimens: Path | str,
    output: Path | str | None = None,
) -> sqlite3.Connection | None:
    """Create a SQLite database from CSV files.

    Parameters:
        persons: Path to persons CSV file
        specimens: Path to specimens CSV file
        output: Path to database file to create or None for in-memory database

    Returns:
        sqlite3.Connection: Database connection if database is in-memory or None otherwise
    """
    if output is None:
        conn = sqlite3.connect(":memory:")
    else:
        Path(output).unlink(missing_ok=True)
        conn = sqlite3.connect(output)

    cursor = conn.cursor()

    for filepath, header, create, insert in (
        (assays, ASSAYS_HEADER, ASSAYS_CREATE, ASSAYS_INSERT),
        (persons, PERSONS_HEADER, PERSONS_CREATE, PERSONS_INSERT),
        (specimens, SPECIMENS_HEADER, SPECIMENS_CREATE, SPECIMENS_INSERT),
    ):
        with open(filepath, "r") as stream:
            data = [row for row in csv.reader(stream)]
            assert data[0] == header
            cursor.execute(create)
            cursor.executemany(insert, data[1:])

    conn.commit()

    if output is None:
        return conn
    else:
        conn.close()
        return None
