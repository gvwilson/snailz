"""Data generation utilities."""

from contextlib import contextmanager
from datetime import date, timedelta
import json
import math
from pathlib import Path
import random
import sys

from pydantic import BaseModel

METERS_PER_DEGREE_LAT = 111_320.0


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


def grid_lat_lon(params, grid, x, y):
    """Calculate latitude and longitude of grid cell."""

    lat = grid.lat0 + (y * params.grid_spacing) / METERS_PER_DEGREE_LAT
    meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(grid.lat0))
    lon = grid.lon0 + (x * params.grid_spacing) / meters_per_degree_lon
    return lat, lon


def grid_origins(params):
    """
    Generate non-overlapping lower-left (lat, lon) corners for grids.
    """

    grid_width_m = params.grid_size * params.grid_spacing
    stride_m = grid_width_m + params.grid_gap_m
    cols = math.ceil(math.sqrt(params.num_grids))
    meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(params.lat0))

    origins = []
    for i in range(params.num_grids):
        dx = (i % cols) * stride_m
        dy = (i // cols) * stride_m
        origins.append(
            (params.lat0 + dy / METERS_PER_DEGREE_LAT, params.lon0 + dx / meters_per_degree_lon)
        )

    return origins


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
