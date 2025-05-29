"""Utilities."""

from datetime import date
import json

from PIL.Image import Image as PilImage
from pydantic import BaseModel


# Floating point decimals for output
PRECISION = 2


def generic_id_generator(id_func):
    """Parameterized ID generator.

    Parameters:
        id_func (callable): function to generate a single ID

    Returns:
        (generator): ID generator.
    """

    current = 0
    while True:
        current += 1
        yield id_func(current)


def json_dump(obj, indent=2):
    """Dump as JSON with appropriate settings.

    Parameters:
        obj (any): The object to serialize
        indent (int | None): Indentation (None for none)

    Returns:
        (str): JSON representation of object.
    """

    return json.dumps(obj, indent=indent, default=_serialize_json)


def max_grid_value(grids):
    """Find maximum value across a list of grids."""

    result = 0.0
    for g in grids:
        for x in range(g.size):
            for y in range(g.size):
                result = max(result, g[x, y])
    return result


def _serialize_json(obj):
    """Custom JSON serializer for JSON conversion.

    Parameters:
        obj (any): The object to serialize

    Returns:
        (str | None): string representation or None.

    Raises:
        TypeError: If the object type is not supported for serialization
    """

    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, PilImage):
        return None
    raise TypeError(f"Type {type(obj)} not serializable")
