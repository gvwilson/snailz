"""Utilities."""

from datetime import date, timedelta
import math
import random
from sqlite_utils import Database
from typing import Any, ClassVar, Generator


# Convert lat/lon to distances.
METERS_PER_DEGREE_LAT = 111_320.0

# Make lat/lon realistic by rounding to 5 decimal places (2m accuracy).
LAT_LON_PRECISION = 5

# Type definitions.
IdGeneratorType = ClassVar[Generator[str, None, None]]
ForeignKeysType = ClassVar[list[tuple[str, str, str]]]


class UnquotedDatabase(Database):
    """Patch sqlite-utils database to avoid quoting."""

    def execute(self, sql: str, parameters: Any = None) -> Any:
        """
        Rewrite `CREATE` statements to remove quoting.

        Args:
            sql: SQL text.
            parameters: Extra arguments.

        Returns:
            A result.
        """

        if sql.strip().upper().startswith("CREATE"):
            sql = sql.replace('"', "")
        return super().execute(sql, parameters)


def id_generator(stem: str, digits: int) -> str:
    """
    Generate unique IDs of the form 'stemDDDD'.

    Args:
        stem: Distinguishing prefix.
        digits: Number of digits in IDs.

    Returns:
        Sequence of IDs.
    """

    i = 1
    while True:
        temp = str(i)
        assert len(temp) <= digits, f"ID generation overflow {stem}: {i}"
        yield f"{stem}{temp.zfill(digits)}"
        i += 1


def lat_lon(
    lat0: float, lon0: float, x_offset_m: float, y_offset_m: float
) -> tuple[float, float]:
    """
    Calculate latitude and longitude from a base point with offsets.

    Args:
        lat0: Reference latitude.
        lon0: Reference longitude.
        x_offset_m: X offset (m).
        y_offset_m: Y offset (m).

    Returns:
        `(lat, lon)` pair.
    """

    lat = lat0 + y_offset_m / METERS_PER_DEGREE_LAT
    m_per_deg_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(lat0))
    lon = lon0 + x_offset_m / m_per_deg_lon
    return round(lat, LAT_LON_PRECISION), round(lon, LAT_LON_PRECISION)


def random_date(min_date: date, max_date: date) -> date:
    """
    Select random date in range (inclusive).

    Args:
        min_date: Start of range.
        max_date: End of range.

    Returns:
        Random date in range.
    """

    days = (max_date - min_date).days
    return min_date + timedelta(days=random.randint(0, days))


def validate(cond: bool, msg: str):
    """
    Validate a condition.

    Args:
        cond: What to check.
        msg: What to report if condition is untrue.

    Raises:
        ValueError: If condition is untrue.
    """

    if not cond:
        raise ValueError(msg)


def validate_lat_lon(caller: str, lat: float, lon: float):
    """
    Validate latitude and longitude.

    Args:
        caller: Name of calling function.
        lat: Latitude.
        lon: Longitude.

    Raises:
        ValueError: If `(lat, lon)` pair is invalid.
    """

    validate(-90.0 <= lat <= 90.0, f"invalid {caller} latitutde {lat}")
    validate(-180.0 <= lon <= 180.0, f"invalid {caller} longitude {lon}")
