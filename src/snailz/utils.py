"""Utilities."""

import csv
from datetime import date, timedelta
import json
import math
from pathlib import Path
import random


# Standard deviation for randomization.
GRID_STD_DEV = 0.5

# Convert lat/lon to distances.
METERS_PER_DEGREE_LAT = 111_320.0

# Make lat/lon realistic by rounding to 5 decimal places (2m accuracy).
LAT_LON_PRECISION = 5

# Mass and diameter precision.
SPECIMEN_PRECISION = 1

# Indentation for JSON output.
JSON_INDENT = 2


class BaseMixin:
    """Mixin base for dataclasses."""

    def as_json(self, indent=JSON_INDENT):
        return json.dumps(self.persistable(), indent=indent, default=_serialize_json)

    def persistable(self):
        """Create persistable dictionary from object."""

        return {key: self.__dict__[key] for key in self.persistable_keys()}

    def persistable_keys(self):
        """Generate list of keys to persist for object."""

        pivot_keys = getattr(self, "pivot_keys", [])
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

    @classmethod
    def _csv_dict_writer(cls, stream, fieldnames):
        """Construct a CSV dict writer with default properties"""

        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        return writer


def id_generator(stem, digits):
    """Generate unique IDs of the form 'stemDDDD'."""

    i = 1
    while True:
        temp = str(i)
        assert len(temp) <= digits, f"ID generation overflow {stem}: {i}"
        yield f"{stem}{temp.zfill(digits)}"
        i += 1


def lat_lon(lat0, lon0, x_offset_m, y_offset_m):
    """Calculate latitude and longitude."""

    lat = lat0 + y_offset_m / METERS_PER_DEGREE_LAT
    m_per_deg_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(lat0))
    lon = lon0 + x_offset_m / m_per_deg_lon
    return round(lat, LAT_LON_PRECISION), round(lon, LAT_LON_PRECISION)


def random_date(min_date, max_date):
    """Select random date in range (inclusive)."""

    days = (max_date - min_date).days
    return min_date + timedelta(days=random.randint(0, days))


def validate(cond, msg):
    """Validate a constructor condition."""

    if not cond:
        raise ValueError(msg)


def validate_lat_lon(caller, lat, lon):
    """Validate latitude and longitude."""

    validate(-90.0 <= lat <= 90.0, f"invalid {caller} latitutde {lat}")
    validate(-180.0 <= lon <= 180.0, f"invalid {caller} longitude {lon}")


def _serialize_json(obj):
    """Custom JSON serializer."""

    assert isinstance(obj, date)
    return obj.isoformat()
