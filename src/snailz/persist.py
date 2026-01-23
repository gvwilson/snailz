"""Database interface."""

import datetime
import csv
import typing

from . import utils


GRID_CREATE = """
create table grid (
  grid_id text not null,
  x integer not null,
  y integer not null,
  lat real not null,
  lon real not null,
  pollution integer not null
)
"""

GRID_INSERT = """
insert into grid(grid_id, x, y, lat, lon, pollution) values(?, ?, ?, ?, ?, ?)
"""


SQLITE_TYPE = {
    int: "integer",
    float: "real",
    bool: "integer",
    datetime.date: "date",
    str: "text",
}


def grids_to_csv(outdir, grids, tidy_grids):
    """Save grids as CSV."""

    for g in grids:
        with utils.file_or_std(outdir, f"{g.grid_id}.csv", "w") as writer:
            print(g, file=writer)

    with utils.file_or_std(outdir, "grids.csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerows(tidy_grids)


def grids_to_db(cnx, tidy_grids):
    """Save all interesting grid cells in database."""

    cnx.execute(GRID_CREATE)
    cnx.executemany(GRID_INSERT, tidy_grids)
    cnx.commit()


def objects_to_csv(stream, objects):
    """Dump a list of Pydantic objects of the same class to a CSV."""

    assert len(objects) > 0
    fields = _select_fields(objects[0])
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for obj in objects:
        writer.writerow(obj.model_dump(include=fields))


def objects_to_db(cnx, table_name, objects):
    if not objects:
        return

    exemplar = objects[0]
    cls = exemplar.__class__
    fields = _select_fields(exemplar)
    cols = [f"{f} {_sqlite_type(cls, f)}" for f in fields]
    foreign_keys = _get_foreign_keys(cls)

    create_sql = f"create table {table_name} (\n  {',\n  '.join(cols)}{foreign_keys}\n)"
    cnx.execute(create_sql)

    placeholders = ", ".join(["?"] * len(fields))
    insert_sql = (
        f"insert into {table_name} ({', '.join(fields)}) values ({placeholders})"
    )

    field_set = set(fields)
    rows = [
        tuple(obj.model_dump(include=field_set)[f] for f in fields) for obj in objects
    ]

    cnx.executemany(insert_sql, rows)
    cnx.commit()


def _get_foreign_keys(cls):
    keys = cls.model_config.get("json_schema_extra", {}).get("foreign_key", None)
    if keys is None:
        return ""
    return ",\n  " + ",\n  ".join(
        f"foreign key({key}) references {table}({other})"
        for key, (table, other) in keys.items()
    )


def _select_fields(obj):
    return [f for f in obj.__class__.model_fields.keys() if not f.endswith("_")]


def _sqlite_type(cls, field_name):
    field = cls.model_fields[field_name]

    annotation = field.annotation
    args = typing.get_args(annotation)
    types = args if args else (annotation,)
    nullness = " not null" if type(None) not in types else ""
    types = [t for t in types if t is not type(None)]
    assert len(types) == 1

    keyness = (
        " primary key"
        if (field.json_schema_extra or {}).get("primary_key", False)
        else ""
    )

    return f"{SQLITE_TYPE[types[0]]}{nullness}{keyness}"
