"""Save data in SQLite database."""

import csv
import sqlite3
from pathlib import Path

from typing import Callable

from . import utils
from .assays import NUM_ASSAY_HEADER_ROWS


ASSAYS = (
    ("ident", "text primary key"),
    ("specimen", "text not null"),
    ("person", "text not null"),
    ("performed", "text"),
    ("machine", "text"),
)

MACHINES = (
    ("ident", "text primary key"),
    ("name", "text not null"),
)

PERSONS = (
    ("ident", "text primary key"),
    ("personal", "text not null"),
    ("family", "text not null"),
)

READINGS = (
    ("ident", "text not null"),
    ("row", "integer not null"),
    ("col", "text not null"),
    ("reading", "real not null"),
)

SPECIMENS = (
    ("ident", "text primary key"),
    ("survey", "text not null"),
    ("x", "integer real not null"),
    ("y", "integer real not null"),
    ("collected", "text not null"),
    ("genome", "text not null"),
    ("mass", "real not null"),
)

TREATMENTS = (
    ("ident", "text not null"),
    ("row", "integer not null"),
    ("col", "text not null"),
    ("treatment", "text not null"),
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
        db_path = root / db_file  # pragma: no cover
        Path(db_path).unlink(missing_ok=True)  # pragma: no cover
        conn = sqlite3.connect(db_path)  # pragma: no cover

    cursor = conn.cursor()

    _import_single_files(root, cursor)
    _import_assay_files(
        root,
        cursor,
        "*_treatments.csv",
        _make_create("treatments", TREATMENTS),
        _make_insert("treatments", TREATMENTS),
        lambda v: v,
    )
    _import_assay_files(
        root,
        cursor,
        "*_readings.csv",
        _make_create("readings", READINGS),
        _make_insert("readings", READINGS),
        lambda v: float(v),
    )

    conn.commit()

    if db_file is None:
        return conn
    else:
        conn.close()  # pragma: no cover
        return None  # pragma: no cover


def _import_assay_files(
    root: Path,
    cursor: sqlite3.Cursor,
    pattern: str,
    create: str,
    insert: str,
    convert: Callable,
) -> None:
    """Import data from all clean assay files.

    Parameters:
        root: path to root directory
        cursor: database cursor
        pattern: filename pattern
        create: SQL table creation statement
        insert: SQL insertion statement
        convert: text-to-value conversion function
    """
    cursor.execute(create)
    for filename in (root / utils.ASSAYS_DIR).glob(pattern):
        with open(filename, "r") as stream:
            rows = [r for r in csv.reader(stream)]
            assert rows[0][0] == "id"
            ident = rows[0][1]
            data = [r[1:] for r in rows[NUM_ASSAY_HEADER_ROWS:]]
            temp = []
            for i, row in enumerate(data):
                for j, val in enumerate(row):
                    temp.append((ident, i + 1, chr(ord("A") + j), convert(val)))
            cursor.executemany(insert, temp)


def _import_single_files(root: Path, cursor: sqlite3.Cursor) -> None:
    """Import single CSV files into database.

    Parameters:
        root: path to root directory
        cursor: database cursor
    """
    for filename, table, spec in (
        (utils.ASSAYS_CSV, "assays", ASSAYS),
        (utils.MACHINES_CSV, "machines", MACHINES),
        (utils.PERSONS_CSV, "persons", PERSONS),
        (utils.SPECIMENS_CSV, "specimens", SPECIMENS),
    ):
        filepath = root / filename
        with open(filepath, "r") as stream:
            data = [row for row in csv.reader(stream)]
            assert data[0] == _make_header(spec)
            cursor.execute(_make_create(table, spec))
            cursor.executemany(_make_insert(table, spec), data[1:])


def _make_create(table: str, spec: tuple) -> str:
    """Generate SQL table creation statement.

    Parameters:
        table: database table name
        spec: tuples of (field name, field properties)

    Returns:
        SQL table creation statement
    """
    fields = ", ".join(f"{name} {props}" for name, props in spec)
    return f"create table {table}({fields})"


def _make_header(spec: tuple) -> list[str]:
    """Generate expected CSV header row.

    Parameters:
        spec: tuples of (field name, field properties)

    Returns:
        Expected first row of CSV file.
    """
    return [name for name, _ in spec]


def _make_insert(table: str, spec: tuple) -> str:
    """Generate SQL insertion statement.

    Parameters:
        table: database table name
        spec: tuples of (field name, field properties)

    Returns:
        SQL record insertion statement
    """
    return f"insert into {table} values ({', '.join('?' * len(spec))})"
