"""Schema keyword data is not a remote-reference instruction."""

from __future__ import annotations

import unittest

from app.models.schema_document import require_local_references


class SchemaDocumentTests(unittest.TestCase):
    def test_literal_keyword_data_is_preserved(self) -> None:
        require_local_references(
            {
                "type": "object",
                "default": {"$ref": "https://literal"},
                "examples": [{"$id": "literal"}],
                "properties": {"$ref": {"type": "string"}},
                "const": {"items": 5},
            }
        )

    def test_escaped_and_percent_encoded_local_references(self) -> None:
        require_local_references(
            {
                "definitions": {"a/b~c": {"type": "string"}},
                "$ref": "#/definitions/a~1b~0c",
            }
        )
        require_local_references(
            {"definitions": {"space key": False}, "$ref": "#/definitions/space%20key"}
        )
        require_local_references(
            {"type": "object", "properties": {"next": {"$ref": "#"}}}
        )

    def test_external_and_unresolved_references_fail(self) -> None:
        for reference in (
            "https://remote",
            "#/missing",
            "#anchor",
            "#/bad~2",
            "#/bad%xx",
        ):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                require_local_references({"$ref": reference})
        with self.assertRaises(ValueError):
            require_local_references({"const": {"type": "string"}, "$ref": "#/const"})

    def test_nested_resource_scope_and_malformed_schema_fail(self) -> None:
        schemas: tuple[dict[str, object], ...] = (
            {"properties": {"child": {"$id": "nested"}}},
            {"$anchor": "x"},
            {"allOf": {}},
            {"properties": []},
        )
        for schema in schemas:
            with self.subTest(schema=schema), self.assertRaises(ValueError):
                require_local_references(schema)

    def test_dependency_names_remain_literal_but_schema_dependencies_are_checked(
        self,
    ) -> None:
        require_local_references({"dependencies": {"value": ["$ref", "const"]}})
        with self.assertRaises(ValueError):
            require_local_references(
                {"dependencies": {"value": {"$ref": "https://remote"}}}
            )


if __name__ == "__main__":
    unittest.main()
