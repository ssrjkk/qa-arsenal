"""Schema validator using JSON Schema."""

import json
from typing import Any

import jsonschema

from validators.response_validator import ResponseValidator


class SchemaValidator:
    """JSON Schema validator."""

    @staticmethod
    def validate(response: ResponseValidator, schema: dict) -> None:
        """Validate response against JSON schema."""
        try:
            jsonschema.validate(instance=response.json, schema=schema)
        except jsonschema.ValidationError as e:
            raise AssertionError(f"Schema validation failed: {e.message}")

    @staticmethod
    def is_valid_json(raw_response: Any, schema: dict) -> bool:
        """Check if raw response is valid JSON."""
        try:
            data = json.loads(raw_response.text) if hasattr(raw_response, "text") else raw_response
            jsonschema.validate(instance=data, schema=schema)
            return True
        except Exception:
            return False
