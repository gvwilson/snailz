"""Data generation utilities."""

from contextlib import contextmanager
from datetime import date, timedelta
import json
from pathlib import Path
import random
import sys

from pydantic import BaseModel


def ensure_id_generator(cls):
    """Ensure class has ID generator."""

    if not hasattr(cls, "_id_gen"):
        cls._id_gen = id_gen(cls.id_stem, cls.id_digits)


@contextmanager
def file_or_std(parent, filename, mode):
    """Open file and return handle or return stdin/stdout."""

    if parent:
        stream = open(Path(parent, filename), mode)
        try:
            yield stream
        finally:
            stream.close()
    elif mode == "r":
        yield sys.stdin
    elif mode == "w":
        yield sys.stdout
    else:
        raise ValueError(f"bad filename/mode '{filename}' / '{mode}'")


def id_gen(stem, digits):
    """Generate unique IDs of the form 'stemDDDD'."""

    i = 1
    while True:
        temp = str(i)
        assert len(temp) <= digits, f"ID generation overflow {stem}: {i}"
        yield f"{stem}{temp.zfill(digits)}"
        i += 1


def json_dump(obj, indent=2):
    """Dump as JSON with custom serializer."""

    return json.dumps(obj, indent=indent, default=_serialize_json)


def random_date(params):
    """Select random date in range (inclusive)."""

    days = (params.sample_date[1] - params.sample_date[0]).days
    return params.sample_date[0] + timedelta(days=random.randint(0, days))


def random_mass(params):
    """Generate random sample mass."""

    return random.uniform(
        params.sample_mass[0],
        params.sample_mass[1],
    )


def _serialize_json(obj):
    """Custom JSON serializer."""

    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise TypeError(f"Type {type(obj)} not serializable")
