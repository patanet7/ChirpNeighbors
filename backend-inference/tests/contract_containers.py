"""Narrow raw fixture containers without duplicating domain/schema admission rules.

Negative contract cases deliberately contain invalid fields and values, so their
mutable pre-validation representation is dict[str, object], not a domain model.
"""

from typing import cast


def object_at(value: object, *path: str | int) -> dict[str, object]:
    """Locate a mutable JSON object, failing on an unexpected fixture shape."""
    for key in path:
        if isinstance(key, str):
            value = object_at(value)[key]
        else:
            if not isinstance(value, list):
                raise TypeError("Fixture path requires an array")
            value = value[key]
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError("Fixture path requires an object with string keys")
    # The key check above proves this container shape; its values remain unknown.
    return cast(dict[str, object], value)


def text(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("Fixture value requires a string")
    return value
