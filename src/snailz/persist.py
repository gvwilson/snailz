"""Database interface."""

import datetime
import csv
import sqlite3
import typing


SQLITE_TYPE = {
    int: "integer",
    float: "real",
    bool: "integer",
    datetime.date: "date",
    str: "text"
}


def models_to_csv(stream, objects):
    """Dump a list of Pydantic objects of the same class to a CSV."""

    assert len(objects) > 0
    fields = _select_fields(objects[0])
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for obj in objects:
        writer.writerow(obj.model_dump(include=fields))


def models_to_db(cnx, table_name, objects):
    if not objects:
        return

    model_cls = type(objects[0])
    fields = _select_fields(objects[0])
    cols = [f"{f} {_sqlite_type(model_cls, f)}" for f in fields]

    create_sql = f"create table if not exists {table_name} ({', '.join(cols)})"
    cnx.execute(create_sql)

    placeholders = ", ".join(["?"] * len(fields))
    insert_sql = f"insert into {table_name} ({', '.join(fields)}) values ({placeholders})"

    field_set = set(fields)
    rows = [
        tuple(obj.model_dump(include=field_set)[f] for f in fields)
        for obj in objects
    ]

    cnx.executemany(insert_sql, rows)
    cnx.commit()


def _select_fields(obj):
    return [f for f in obj.__class__.model_fields.keys() if not f.endswith("_")]


def _sqlite_type(cls, field_name):
    annotation = cls.model_fields[field_name].annotation
    args = typing.get_args(annotation)
    types = args if args else (annotation,)
    types = [t for t in types if t is not type(None)]
    assert len(types) == 1
    return SQLITE_TYPE[types[0]]
