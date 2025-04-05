"""Snailz utilities."""

import csv
from datetime import date
import io
import json
import sys
from typing import Callable

from pydantic import BaseModel


# Floating point precision.
PRECISION = 2

# Maximum tries to generate a unique ID.
UNIQUE_ID_LIMIT = 10_000

# Default survey grid size.
DEFAULT_SURVEY_SIZE = 15

# File paths
ASSAYS_CSV = "assays.csv"
ASSAYS_DIR = "assays"
PERSONS_CSV = "persons.csv"
SPECIMENS_CSV = "specimens.csv"
SURVEYS_DIR = "surveys"


class UniqueIdGenerator:
    """Generate unique IDs using provided function."""

    def __init__(self, name: str, func: Callable, limit: int = UNIQUE_ID_LIMIT) -> None:
        """Initialize.

        Parameters:
            name: A name for this generator
            func: Function that creates IDs when called
            limit: Maximum number of attempts
        """
        self._name = name
        self._func = func
        self._limit = limit
        self._seen = set()

    def next(self, *args: object) -> str:
        """Get next unique ID.

        Parameters:
            args: Arguments to pass to the ID-generating function

        Returns:
            A unique identifier that hasn't been returned before

        Raises:
            RuntimeError: If unable to generate a unique ID within limit attempts
        """
        for i in range(self._limit):
            ident = self._func(*args)
            if ident in self._seen:
                continue
            self._seen.add(ident)
            return ident
        raise RuntimeError(f"failed to find unique ID for {self._name}")


def display(filepath: str | None, data: BaseModel | str) -> None:
    """Write to a file or to stdout.

    Parameters:
        filepath: Output filepath or None for stdout
        data: what to write
    """
    if isinstance(data, str):
        text = data
    else:
        text = json.dumps(data, indent=2, default=_serialize_json)

    if not filepath:
        print(text)
    else:
        with open(filepath, "w") as writer:
            writer.write(text)


def fail(msg: str) -> None:
    """Report failure and exit.

    Parameters:
        msg: Error message to display
    """
    print(msg, file=sys.stderr)
    sys.exit(1)


def report(verbose: bool, msg: str) -> None:
    """Report if verbosity turned on.

    Parameters:
        verbose: Is display on or off?
        msg: Message to display
    """
    if verbose:
        print(msg)


def to_csv(rows: list, fields: list, f_make_row: Callable) -> str:
    """Generic converter from list of models to CSV string.

    Parameters:
        rows: List of rows to convert.
        fields: List of names of columns.
        f_make_row: Function that converts a row to text.

    Returns:
        CSV representation of data.
    """

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(fields)
    for r in rows:
        writer.writerow(f_make_row(r))
    return output.getvalue()


def _serialize_json(obj: object) -> str | dict:
    """Custom JSON serializer for JSON conversion.

    Parameters:
        obj: The object to serialize

    Returns:
        String representation of date objects or dict for Pydantic models

    Raises:
        TypeError: If the object type is not supported for serialization
    """
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise TypeError(f"Type {type(obj)} not serializable")
