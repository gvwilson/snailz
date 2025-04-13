#!/usr/bin/env python

"""doit commands for snailz project"""

from pathlib import Path
import shutil


# Which tasks are run by default.
DOIT_CONFIG = {
    "default_tasks": [],
    "verbosity": 2,
}

# Directories and files to clean during the build process.
DIRS_TO_TIDY = ["build", "dist", "*.egg-info"]

# Directories and files.
DATA_DIR = Path("data")
DATA_ZIP = Path("snailz.zip")
PARAMS_JSON = DATA_DIR / "params.json"
SCRIPTS_DIR = Path("scripts")
TMP_DIR = Path("tmp")


def task_build():
    """Build the Python package."""

    return {
        "actions": [
            "python -m build",
            "twine check dist/*",
        ],
        "task_dep": ["tidy"],
    }


def task_classify():
    """Classify assay results."""

    return {
        "actions": [
            f"python {SCRIPTS_DIR}/classify.py --data {DATA_DIR} --format df",
        ],
    }


def task_coverage():
    """Run tests with coverage."""

    return {
        "actions": [
            "python -m coverage run -m pytest tests",
            "python -m coverage report --show-missing",
        ],
    }


def task_data():
    """Rebuild all data."""

    return {
        "actions": [
            f"rm -rf {DATA_DIR}/*",
            f"mkdir -p {DATA_DIR}",
            f"snailz params --output {PARAMS_JSON}",
            f"snailz data --params {PARAMS_JSON} --output {DATA_DIR}",
        ],
    }


def task_db():
    """Create database from generated data."""

    return {
        "actions": [
            f"snailz db --data {DATA_DIR}",
        ],
    }


def task_docs():
    """Generate documentation using MkDocs."""

    return {
        "actions": [
            "mkdocs build",
        ],
    }


def task_format():
    """Reformat code."""

    return {
        "actions": [
            "ruff format .",
        ],
    }


def task_lims_run():
    """Run the LIMS."""

    return {
        "actions": [
            f"python lims/app.py --data {DATA_DIR} --memory",
        ],
    }


def task_lims_test():
    """Run the LIMS tests."""

    return {
        "actions": [
            "pytest lims/test_*.py --data data",
        ],
    }


def task_lint():
    """Check the code format and typing."""

    return {
        "actions": [
            "ruff check .",
            "pyright",
        ],
    }


def task_site():
    """Serve documentation website."""

    return {
        "actions": [
            "mkdocs serve",
        ],
    }


def task_test():
    """Run tests."""
    return {
        "actions": [
            "python -m pytest tests",
        ],
    }


def task_tidy():
    """Clean all build artifacts."""

    return {
        "actions": [
            _tidy_directories,
        ],
    }


def task_vis_grids():
    """Visualize grids."""

    return {
        "actions": [
            f"mkdir -p {TMP_DIR}",
            f"python {SCRIPTS_DIR}/visualize.py --data {DATA_DIR} --make grid --output {TMP_DIR}/grids.png --show",
        ],
    }


def task_zip():
    """Create ZIP file from generated data."""

    return {
        "actions": [
            f"snailz zip --data {DATA_DIR} --output {DATA_ZIP}",
        ],
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
