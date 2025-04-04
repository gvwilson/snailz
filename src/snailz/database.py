"""Save data in SQLite database."""

import csv
import sqlite3
from pathlib import Path

PEOPLE_CREATE = """
create table people (
    ident text primary key,
    personal text,
    family text
)
"""
PEOPLE_HEADER = ["ident", "personal", "family"]
PEOPLE_INSERT = f"insert into people values ({', '.join('?' * len(PEOPLE_HEADER))})"

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
SPECIMENS_INSERT = f"insert into specimens values ({', '.join('?' * len(SPECIMENS_HEADER))})"


def database_generate(
    people: Path | str,
    specimens: Path | str,
    output: Path | str | None = None,
) -> sqlite3.Connection | None:
    """Create a SQLite database from CSV files.

    Parameters:
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
