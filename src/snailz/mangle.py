"""Modify assay CSV files to simulate poor formatting."""

import csv
from pathlib import Path
import random

from .persons import Person, AllPersons


ORIGINAL = "_readings"
MANGLED = "_raw"


def mangle_assays(
    assays_dir: Path | str, persons: AllPersons, forced: list[str] | None = None
) -> None:
    """Create 'raw' assay files by mangling data of pristine files.

    Parameters:
        assays_dir: Directory containing assay CSV files
        persons: People who performed experiments
        forced: names of changes to apply (select randomly if None)

    Raises:
        ValueError: If people data cannot be loaded
    """
    staff = {p.ident: p for p in persons.items}
    for filename in Path(assays_dir).glob(f"*{ORIGINAL}.csv"):
        with open(filename, "r") as stream:
            original = [row for row in csv.reader(stream)]
        mangled = _mangle_assay(original, staff, forced)
        output_file = str(filename).replace(f"{ORIGINAL}.csv", f"{MANGLED}.csv")
        with open(output_file, "w") as stream:
            csv.writer(stream, lineterminator="\n").writerows(mangled)


def _mangle_assay(
    data: list[list[str]], staff: dict[str, Person], forced: list[str] | None
) -> list[list]:
    """Mangle a single assay file.

    Parameters:
        data: values from CSV file
        staff: people keyed by ID
        forced: optional list of specified manglings (for testing)

    Returns:
        Modified copy of data.
    """
    available = {
        "id": _mangle_id,
        "indent": _mangle_indent,
        "person": _mangle_person,
    }

    if forced is None:
        num_mangles = random.randint(0, len(available))
        manglers = random.sample(list(available.values()), num_mangles)
    else:
        manglers = [available[name] for name in forced]

    for func in manglers:
        data = func(data, staff)
    return data


def _mangle_id(data: list[list[str]], staff: dict[str, Person]) -> list[list[str]]:
    """Convert ID field to string.

    Parameters:
        data: values from CSV file
        staff: people keyed by ID

    Returns:
        Modified copy of data.
    """
    for row in data:
        if any(x == "id" for x in row):
            i = row.index("id")
            row[i + 1] = f"'{row[i + 1]}'"
    return data


def _mangle_indent(data: list[list], staff: dict[str, Person]) -> list[list[str]]:
    """Indent data portion.

    Parameters:
        data: values from CSV file
        staff: people keyed by ID

    Returns:
        Modified copy of data.
    """
    return [
        ([""] + row)
        if (row[0].isdigit() or (row[0] == "" and row[1] == "A"))
        else (row + [""])
        for row in data
    ]


def _mangle_person(data: list[list], staff: dict[str, Person]) -> list[list[str]]:
    """Replace person identifier with name.

    Parameters:
        data: values from CSV file
        staff: people keyed by ID

    Returns:
        Modified copy of data.
    """
    for row in data:
        if row[0] == "by":
            row[0] = "performed"
            person = staff[row[1]]
            row[1] = f"{person.personal} {person.family}"
    return data
