"""Modify assay CSV files to simulate poor formatting."""

import csv
import json
from pathlib import Path
import random

from . import utils


def mangle_assays(assays_dir: str, people_file: str) -> None:
    """Create 'raw' assay files by mangling data of pristine files.

    Parameters:
        assays_dir: Directory containing assay CSV files
        people_file: Path to the people JSON file

    Raises:
        ValueError: If people data cannot be loaded or no people are found
    """
    people = _load_people(people_file)
    for filename in Path(assays_dir).glob("*_assay.csv"):
        with open(filename, "r") as stream:
            original = [row for row in csv.reader(stream)]
        mangled = _mangle_assay(people, original)
        output_file = str(filename).replace("_assay.csv", "_raw.csv")
        with open(output_file, "w") as stream:
            csv.writer(stream, **utils.CSV_SETTINGS).writerows(mangled)


def _load_people(filename: str) -> dict[str, dict]:
    """Read people and rearrange to {ident: data} dictionary."""
    try:
        with open(filename, "r") as reader:
            people_data = json.load(reader)
            return {p["ident"]: p for p in people_data["individuals"]}
    except Exception as e:
        raise ValueError(f"Error loading people data: {str(e)}")


def _mangle_assay(people: dict[str, dict], data: list[list]) -> list[list]:
    """Mangle a single assay file."""
    manglers = [_mangle_id, _mangle_indent, _mangle_person]
    num_mangles = random.randint(0, len(manglers))
    for func in random.sample(manglers, num_mangles):
        data = func(data, people)
    return data


def _mangle_id(data: list[list], people: dict[str, dict]) -> list[list]:
    """Convert ID field to string."""
    for row in data:
        if any(x == "id" for x in row):
            i = row.index("id")
            row[i + 1] = f"'{row[i + 1]}'"
    return data


def _mangle_indent(data: list[list], people: dict[str, dict]) -> list[list]:
    """Indent data portion."""
    return [([""] + row) if row[0].isdigit() else (row + [""]) for row in data]


def _mangle_person(data: list[list], people: dict[str, dict]) -> list[list]:
    """Replace person identifier with name."""
    for row in data:
        if row[0] == "performed_by":
            person = people[row[1]]
            row[1] = f"{person['personal']} {person['family']}"
    return data
