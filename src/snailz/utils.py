"""Snailz utilities."""

import csv
import io
import sys


# Maximum tries to generate a unique ID.
UNIQUE_ID_LIMIT = 10_000


class UniqueIdGenerator:
    """Generate unique IDs using provided function."""

    def __init__(self, name, func, limit=UNIQUE_ID_LIMIT):
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

    def next(self, *args):
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


def display(stream, text):
    """Write to a file or to stdout."""
    if not stream:
        print(text)
    else:
        with open(stream, "w") as writer:
            writer.write(text)


def fail(msg):
    """Report failure and exit."""
    print(msg, file=sys.stderr)
    sys.exit(1)


def report(verbose, msg):
    """Report if verbosity turned on."""
    if verbose:
        print(msg)


def to_csv(rows, fields, f_make_row):
    """Generic converter from list of models to CSV string."""

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(fields)
    for r in rows:
        writer.writerow(f_make_row(r))
    return output.getvalue()
