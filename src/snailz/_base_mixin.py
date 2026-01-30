"""Utilities for dataclasses."""

import csv
from datetime import date
import json
from pathlib import Path


# Indentation for JSON output.
JSON_INDENT = 2


class BaseMixin:
    """Mixin base for dataclasses."""

    def as_json(self, indent=JSON_INDENT):
        return json.dumps(self.persistable(), indent=indent, default=_serialize_json)

    def persistable(self):
        """Create persistable dictionary from object."""

        return {key: self.__dict__[key] for key in self.persistable_keys()}

    def not_null_keys(self):
        """Generate list of non-null keys for object."""

        nullable_keys = getattr(self, "nullable_keys", set())
        return {key for key in self.persistable_keys() if key not in nullable_keys}

    def persistable_keys(self):
        """Generate list of keys to persist for object."""

        pivot_keys = getattr(self, "pivot_keys", set())
        return [key for key in self.__dict__.keys() if key not in pivot_keys]

    @classmethod
    def save_csv(cls, outdir, objects):
        """Save objects as CSV."""

        assert all(isinstance(obj, cls) for obj in objects)
        with open(Path(outdir, f"{cls.table_name}.csv"), "w", newline="") as stream:
            writer = cls._csv_dict_writer(stream, objects[0].persistable_keys())
            for obj in objects:
                writer.writerow(obj.persistable())

    @classmethod
    def save_db(cls, db, objects):
        """Save objects to database."""

        assert all(isinstance(obj, cls) for obj in objects)
        table = db[cls.table_name]
        primary_key = getattr(cls, "primary_key", None)
        foreign_keys = getattr(cls, "foreign_keys", [])
        table.insert_all(
            (obj.persistable() for obj in objects),
            pk=primary_key,
            foreign_keys=foreign_keys,
        )
        table.transform(not_null=objects[0].not_null_keys())

    @classmethod
    def _csv_dict_writer(cls, stream, fieldnames):
        """Construct a CSV dict writer with default properties"""

        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        return writer


def _serialize_json(obj):
    """Custom JSON serializer."""

    assert isinstance(obj, date)
    return obj.isoformat()
