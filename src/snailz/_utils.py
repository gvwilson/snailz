"""Utilities."""

from datetime import timedelta
import math
import random
import sqlite_utils


# Convert lat/lon to distances.
METERS_PER_DEGREE_LAT = 111_320.0

# Make lat/lon realistic by rounding to 5 decimal places (2m accuracy).
LAT_LON_PRECISION = 5


class UnquotedDatabase(sqlite_utils.Database):
    def execute(self, sql, parameters=None):
        if sql.strip().upper().startswith("CREATE"):
            sql = sql.replace('"', "")
        return super().execute(sql, parameters)


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
