"""Snailz utilities."""

import sys


def fail(msg):
    """Report failure and exit."""
    print(msg, file=sys.stderr)
    sys.exit(1)


def report(verbose, msg):
    """Report if verbosity turned on."""
    if verbose:
        print(msg)
