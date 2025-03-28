#!/usr/bin/env python

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
PARAMS_DIR = Path("params")
OUT_DIR = Path("tmp")
ASSAYS_PARAMS = str(PARAMS_DIR / "assays.json")
ASSAYS_JSON = str(OUT_DIR / "assays.json")
GRID_PARAMS = str(PARAMS_DIR / "grid.json")
GRID_JSON = str(OUT_DIR / "grid.json")
GRID_CSV = str(OUT_DIR / "grid.csv")
PEOPLE_PARAMS = str(PARAMS_DIR / "people.json")
PEOPLE_JSON = str(OUT_DIR / "people.json")
PEOPLE_CSV = str(OUT_DIR / "people.csv")
SPECIMENS_PARAMS = str(PARAMS_DIR / "specimens.json")
SPECIMENS_JSON = str(OUT_DIR / "specimens.json")
SPECIMENS_CSV = str(OUT_DIR / "specimens.csv")


def task_all():
    """Rebuild all data."""
    return {
        "actions": None,
        "task_dep": ["grid", "specimens", "people", "assays", "mangle"],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_assays():
    """Generate sample assays file."""

    return {
        "actions": [
            f"mkdir -p {OUT_DIR}",
            f"snailz assays --params {ASSAYS_PARAMS} --output {ASSAYS_JSON} --people {PEOPLE_JSON} --specimens {SPECIMENS_JSON}",
            f"snailz convert --kind assays --input {ASSAYS_JSON} --output {OUT_DIR}",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_build():
    """Build the Python package in the current directory."""

    return {
        "actions": [
            "python -m build",
            "twine check dist/*",
        ],
        "task_dep": ["tidy"],
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


def task_grid():
    """Generate sample grid file."""

    return {
        "actions": [
            f"mkdir -p {OUT_DIR}",
            f"snailz grid --params {GRID_PARAMS} --output {GRID_JSON}",
            f"snailz convert --kind grid --input {GRID_JSON} --output {GRID_CSV}",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_init():
    """Initialize parameter files."""

    return {
        "actions": [
            f"snailz init --output {PARAMS_DIR}",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_lint():
    """Check the code format."""

    return {
        "actions": [
            "ruff check .",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_mangle():
    """Mangle generated assay files."""

    return {
        "actions": [
            f"snailz mangle --dir tmp/assays --people {PEOPLE_JSON} --seed 2173498"
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_typing():
    """Check types with pyright."""

    return {
        "actions": [
            "pyright",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_people():
    """Generate sample people file."""

    return {
        "actions": [
            f"mkdir -p {OUT_DIR}",
            f"snailz people --params {PEOPLE_PARAMS} --output {PEOPLE_JSON}",
            f"snailz convert --kind people --input {PEOPLE_JSON} --output {PEOPLE_CSV}",
        ],
        "verbosity": VERBOSITY,
        "uptodate": [False],
    }


def task_specimens():
    """Generate sample specimens file."""

    return {
        "actions": [
            f"mkdir -p {OUT_DIR}",
            f"snailz specimens --params {SPECIMENS_PARAMS} --output {SPECIMENS_JSON} --grid {GRID_JSON}",
            f"snailz convert --kind specimens --input {SPECIMENS_JSON} --output {SPECIMENS_CSV}",
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


def task_docs():
    """Generate documentation using MkDocs."""

    return {
        "actions": [
            "mkdocs build",
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
