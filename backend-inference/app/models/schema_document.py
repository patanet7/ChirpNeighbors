"""Offline schema-reference admission, distinct from literal JSON data validation."""

from __future__ import annotations

import re
from urllib.parse import unquote

_MAPS = frozenset(
    {"properties", "patternProperties", "$defs", "definitions", "dependentSchemas"}
)
_SINGLE = frozenset(
    {
        "additionalProperties",
        "additionalItems",
        "contains",
        "propertyNames",
        "not",
        "if",
        "then",
        "else",
        "unevaluatedProperties",
        "unevaluatedItems",
        "contentSchema",
    }
)
_ARRAYS = frozenset({"allOf", "anyOf", "oneOf", "prefixItems"})


def _pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def require_local_references(document: object) -> None:
    """Reject remote/unresolved/scoped refs without interpreting const/default data.

    Only schema-bearing vocabulary positions are traversed. This helper performs
    offline reference safety checks; the configured JSON Schema validator remains
    responsible for the dialect and all value-validation keywords.
    """
    nodes: set[str] = set()
    references: list[str] = []

    def visit(value: object, path: str) -> None:
        if isinstance(value, bool):
            nodes.add(path)
            return
        if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
            raise ValueError("Schema nodes must be objects or booleans")
        nodes.add(path)
        if path != "#" and ("$id" in value or "$schema" in value):
            raise ValueError("Nested schema resource scopes are unsupported")
        if any(key in value for key in ("$anchor", "$dynamicAnchor", "$dynamicRef")):
            raise ValueError("Schema anchors require an explicit offline resolver")
        if "$ref" in value:
            reference = value["$ref"]
            if not isinstance(reference, str) or not (
                reference == "#" or reference.startswith("#/")
            ):
                raise ValueError(
                    "Only local references using schema JSON Pointers are allowed"
                )
            if re.search(r"%(?![0-9a-fA-F]{2})", reference):
                raise ValueError("Malformed URI reference")
            decoded = unquote(reference, errors="strict")
            if re.search(r"~(?![01])", decoded):
                raise ValueError("Malformed JSON Pointer reference")
            references.append(decoded)
        for key, child in value.items():
            child_path = f"{path}/{_pointer(key)}"
            if key in _MAPS:
                if not isinstance(child, dict):
                    raise ValueError("Schema map must be an object")
                for name, schema in child.items():
                    if not isinstance(name, str):
                        raise ValueError("Schema map key must be a string")
                    visit(schema, f"{child_path}/{_pointer(name)}")
            elif key in _SINGLE:
                visit(child, child_path)
            elif key in _ARRAYS or (key == "items" and isinstance(child, list)):
                if not isinstance(child, list):
                    raise ValueError("Schema combinator must be an array")
                for index, schema in enumerate(child):
                    visit(schema, f"{child_path}/{index}")
            elif key == "items":
                visit(child, child_path)
            elif key == "dependencies":
                if not isinstance(child, dict):
                    raise ValueError("Dependencies must be an object")
                for name, schema in child.items():
                    if not isinstance(name, str):
                        raise ValueError("Dependency key must be a string")
                    if isinstance(schema, list) and all(
                        isinstance(field, str) for field in schema
                    ):
                        continue
                    visit(schema, f"{child_path}/{_pointer(name)}")

    visit(document, "#")
    if any(reference not in nodes for reference in references):
        raise ValueError("Reference must resolve to an actual local schema node")
