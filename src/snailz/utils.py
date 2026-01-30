"""Utilities."""

from datetime import date, timedelta
import json
import math
import random


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
        return json.dumps(self.persist(), indent=indent, default=_serialize_json)

    def persist(self):
        if hasattr(self.__class__, "pivot_keys"):
            return {
                key: value
                for key, value in self.__dict__.items()
                if key not in self.__class__.pivot_keys
            }
        else:
            return self.__dict__

    @classmethod
    def save_db(cls, db, thing):
        """Save objects to database."""

        if isinstance(thing, (list, tuple)):
            assert len(thing) > 0, "cannot persist no objects"
        else:
            thing = [thing]
        table = db[cls.table_name]
        primary_key = getattr(cls, "primary_key", None)
        foreign_keys = getattr(cls, "foreign_keys", [])
        table.insert_all(
            (t.persist() for t in thing),
            pk=primary_key,
            foreign_keys=foreign_keys,
        )


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
