#!/usr/bin/env python

"""doit commands for snailz project"""

from pathlib import Path
import shutil


# Which tasks are run by default.
DOIT_CONFIG = {
    "default_tasks": [],
}

# How noisy to be.
VERBOSITY = 2

# Directories and files to clean during the build process.
DIRS_TO_TIDY = ["build", "dist", "*.egg-info"]

# Directories and files.
TMP_DIR = Path("tmp")
PARAMS_JSON = TMP_DIR / "params.json"
DATA_JSON = TMP_DIR / "data.json"


def task_build():
    """Build the Python package."""

    return {
        "actions": [
            "python -m build",
            "twine check dist/*",
        ],
        "task_dep": ["tidy"],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_coverage():
    """Run tests with coverage."""

    return {
        "actions": [
            "python -m coverage run -m pytest tests",
            "python -m coverage report --show-missing",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_data():
    """Rebuild all data."""

    return {
        "actions": [
            f"mkdir -p {TMP_DIR}",
            f"snailz data --params {PARAMS_JSON} --output {DATA_JSON} --csvdir {TMP_DIR}",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_docs():
    """Generate documentation using MkDocs."""

    return {
        "actions": [
            "mkdocs build",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_format():
    """Reformat code."""

    return {
        "actions": [
            "ruff format .",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_lint():
    """Check the code format and typing."""

    return {
        "actions": [
            "ruff check .",
            "pyright",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_params():
    """Regenerate parameter files."""

    return {
        "actions": [
            f"mkdir -p {TMP_DIR}",
            f"snailz params --output {PARAMS_JSON}",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_test():
    """Run tests."""
    return {
        "actions": [
            "python -m pytest tests",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_tidy():
    """Clean all build artifacts."""

    return {
        "actions": [
            _tidy_directories,
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def _tidy_directories():
    current_dir = Path(".")
    for pattern in DIRS_TO_TIDY:
        for path in current_dir.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    return True
