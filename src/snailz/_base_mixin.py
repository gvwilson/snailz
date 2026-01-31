"""Utility base class for dataclasses."""

from csv import DictWriter
from datetime import date
import json
from pathlib import Path
from sqlite_utils import Database
from typing import Any, TextIO


# Indentation for JSON output.
JSON_INDENT = 2


class BaseMixin:
    """Mixin base class for dataclasses."""

    def as_json(self, indent: int = JSON_INDENT) -> str:
        """
        Convert this object to a JSON string.

        Args:
            indent: Indentation.

        Returns:
            JSON string representation of persistable fields.
        """
        return json.dumps(self.persistable(), indent=indent, default=_serialize_json)

    def persistable(self) -> dict:
        """
        Create persistable dictionary from object by ignoring all keys
        listed in class-level `pivot_keys` member.
        """

        return {key: self.__dict__[key] for key in self.persistable_keys()}

    def not_null_keys(self) -> set:
        """Generate set of keys for non-null values in object."""

        nullable_keys = getattr(self, "nullable_keys", set())
        return {key for key in self.persistable_keys() if key not in nullable_keys}

    def persistable_keys(self) -> list[str]:
        """
        Generate list of keys to persist for object by ignoring all
        keys listed in class-level `pivot_keys` member.
        """

        pivot_keys = getattr(self, "pivot_keys", set())
        return [key for key in self.__dict__.keys() if key not in pivot_keys]

    @classmethod
    def save_csv(cls, outdir: Path | str, objects: list[Any]):
        """
        Save objects of derived class as CSV. Derived classes should
        override this and up-call to save scalar properties, then save
        properties that need to be pivoted to long form.

        Args:
            outdir: Output directory.
            objects: Objects to save.
        """

        assert all(isinstance(obj, cls) for obj in objects)
        with open(Path(outdir, f"{cls.table_name}.csv"), "w", newline="") as stream:
            writer = cls._csv_dict_writer(stream, objects[0].persistable_keys())
            for obj in objects:
                writer.writerow(obj.persistable())

    @classmethod
    def save_db(cls, db: Database, objects: list[Any]):
        """
        Save objects of derived class to database. Derived classes should
        override this and up-call to save scalar properties, then save
        properties that need to be pivoted to long form.

        Args:
            db: Database connector.
            objects: Objects to save.
        """

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
    def _csv_dict_writer(cls, stream: TextIO, fieldnames: list[str]) -> DictWriter:
        """
        Construct a CSV dict writer with default properties.

        Args:
            stream: Writeable stream to wrap.
            fieldnames: List of fields to be persisted.

        Returns:
            CSV dict writer.
        """

        writer = DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        return writer


def _serialize_json(obj: Any) -> Any:
    """
    Custom JSON serializer.

    Args:
        obj: What to persist.

    Returns:
        String representation of object.
    """

    assert isinstance(obj, date)
    return obj.isoformat()
