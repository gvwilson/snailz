"""Create SQLite database from CSV files."""

import csv
import sqlite3
from pathlib import Path

ASSAYS_CREATE = """
create table assays (
    ident text primary key,
    specimen_id text,
    performed text,
    performed_by text,
    foreign key (specimen_id) references specimens(ident),
    foreign key (performed_by) references people(ident)
)
"""
ASSAYS_HEADER = ["ident", "specimen_id", "performed", "performed_by"]
ASSAYS_INSERT = "insert into assays values (?, ?, ?, ?)"

PEOPLE_CREATE = """
create table people (
    ident text primary key,
    personal text,
    family text
)
"""
PEOPLE_HEADER = ["ident", "personal", "family"]
PEOPLE_INSERT = "insert into people values (?, ?, ?)"

SPECIMENS_CREATE = """
create table specimens (
    ident text primary key,
    x integer real not null,
    y integer real not null,
    genome text,
    mass real,
    collected_on text,
    territory real not null
)
"""
SPECIMENS_HEADER = ["ident", "x", "y", "genome", "mass", "collected_on", "territory"]
SPECIMENS_INSERT = "insert into specimens values (?, ?, ?, ?, ?, ?, ?)"


def make_database(
    assays: Path | str,
    people: Path | str,
    specimens: Path | str,
    output: Path | str | None = None,
) -> sqlite3.Connection | None:
    """Create a SQLite database from CSV files.

    Parameters:
        assays: Path to assays CSV file
        people: Path to people CSV file
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
        (people, PEOPLE_HEADER, PEOPLE_CREATE, PEOPLE_INSERT),
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
