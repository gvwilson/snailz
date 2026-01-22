"""Database interface."""

import datetime
import csv
import typing


SQLITE_TYPE = {
    int: "integer",
    float: "real",
    bool: "integer",
    datetime.date: "date",
    str: "text",
}


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

    create_sql = f"create table if not exists {table_name} (\n  {',\n  '.join(cols)}{foreign_keys}\n)"
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
