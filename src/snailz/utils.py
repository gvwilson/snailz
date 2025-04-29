"""Utilities."""

from datetime import date
import json

from PIL.Image import Image as PilImage
from pydantic import BaseModel


# Floating point decimals for output
PRECISION = 2


def generic_id_generator(id_func):
    """Parameterized ID generator."""

    current = 0
    while True:
        current += 1
        yield id_func(current)


def json_dump(obj, indent=2):
    """Dump as JSON with appropriate settings.

    Parameters:
        obj: The object to serialize
        indent: Indentation (None for none)

    Returns:
        String representation of object.
    """

    return json.dumps(obj, indent=indent, default=_serialize_json)


def _serialize_json(obj):
    """Custom JSON serializer for JSON conversion.

    Parameters:
        obj: The object to serialize

    Returns:
        String representation of date objects or dict for Pydantic models;
        None for PIL images.

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
