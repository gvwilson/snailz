"""Modify assay CSV files to simulate poor formatting."""

import csv
import random


def mangle_assay(readings_file, raw_file, persons, forced=None):
    """Mangle a single assay file.

    Parameters:
        readings_file (Path): clean readings file
        raw_file (Path): file to produce
        persons (list[Person]): staff members
        forced (bool): optional list of specified manglings (for testing)
    """
    available = {
        "id": _mangle_id,
        "indent": _mangle_indent,
        "missing": _mangle_missing,
        "person": _mangle_person,
    }

    if forced is None:
        num_mangles = random.randint(0, len(available))
        manglers = random.sample(list(available.values()), num_mangles)
    else:
        manglers = [available[name] for name in forced]

    with open(readings_file, "r") as stream:
        data = [r for r in csv.reader(stream)]
    for func in manglers:
        data = func(data, persons)
    with open(raw_file, "w") as stream:
        csv.writer(stream).writerows(data)


def _mangle_id(data, persons):
    """Convert ID field to string."""

    for row in data:
        if any(x == "id" for x in row):
            i = row.index("id")
            row[i + 1] = f"'{row[i + 1]}'"
    return data


def _mangle_indent(data, persons):
    """Indent data portion."""

    return [
        ([""] + row)
        if (row[0].isdigit() or (row[0] == "" and row[1] == "A"))
        else (row + [""])
        for row in data
    ]


def _mangle_missing(data, persons):
    """Remove machine name (alters length of header)."""

    return [row for row in data if row[0] != "machine"]


def _mangle_person(data, persons):
    """Replace person identifier with name."""

    for row in data:
        if row[0] == "person":
            row[0] = "by"
            person_id = row[1]
            matches = [p for p in persons if p.id == person_id]
            assert len(matches) == 1, f"Bad person ID {person_id} during mangling"
            row[1] = f"{matches[0].personal} {matches[0].family}"
    return data
