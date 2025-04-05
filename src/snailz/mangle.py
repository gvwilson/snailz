"""Modify assay CSV files to simulate poor formatting."""

import csv
from pathlib import Path
import random

from .persons import Person, AllPersons


ORIGINAL = "_readings"
MANGLED = "_raw"


def mangle_assays(assays_dir: Path | str, persons: AllPersons) -> None:
    """Create 'raw' assay files by mangling data of pristine files.

    Parameters:
        assays_dir: Directory containing assay CSV files
        persons: People who performed experiments

    Raises:
        ValueError: If people data cannot be loaded
    """
    staff = {p.ident: p for p in persons.items}
    for filename in Path(assays_dir).glob(f"*{ORIGINAL}.csv"):
        with open(filename, "r") as stream:
            original = [row for row in csv.reader(stream)]
        mangled = _mangle_assay(original, staff)
        output_file = str(filename).replace(f"{ORIGINAL}.csv", f"{MANGLED}.csv")
        with open(output_file, "w") as stream:
            csv.writer(stream, lineterminator="\n").writerows(mangled)


def _mangle_assay(data: list[list[str]], staff: dict[str, Person]) -> list[list]:
    """Mangle a single assay file."""
    manglers = [_mangle_id, _mangle_indent, _mangle_person]
    num_mangles = random.randint(0, len(manglers))
    for func in random.sample(manglers, num_mangles):
        data = func(data, staff)
    return data


def _mangle_id(data: list[list[str]], staff: dict[str, Person]) -> list[list[str]]:
    """Convert ID field to string."""
    for row in data:
        if any(x == "id" for x in row):
            i = row.index("id")
            row[i + 1] = f"'{row[i + 1]}'"
    return data


def _mangle_indent(data: list[list], staff: dict[str, Person]) -> list[list[str]]:
    """Indent data portion."""
    return [([""] + row) if row[0].isdigit() else (row + [""]) for row in data]


def _mangle_person(data: list[list], staff: dict[str, Person]) -> list[list[str]]:
    """Replace person identifier with name."""
    for row in data:
        if row[0] == "by":
            row[0] = "performed"
            person = staff[row[1]]
            row[1] = f"{person.personal} {person.family}"
    return data
