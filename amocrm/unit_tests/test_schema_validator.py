"""Hermetic unit tests for the JSON-schema validator (no network)."""

import json

import pytest

from validators.schema_validator import SchemaValidator

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
    },
}


class FakeRaw:
    def __init__(self, text):
        self.text = text


class TestIsValidJson:
    def test_valid_payload(self):
        raw = FakeRaw(json.dumps({"id": 1, "name": "alice"}))
        assert SchemaValidator.is_valid_json(raw, USER_SCHEMA) is True

    def test_missing_required_field(self):
        raw = FakeRaw(json.dumps({"id": 1}))
        assert SchemaValidator.is_valid_json(raw, USER_SCHEMA) is False

    def test_wrong_type(self):
        raw = FakeRaw(json.dumps({"id": "x", "name": "alice"}))
        assert SchemaValidator.is_valid_json(raw, USER_SCHEMA) is False

    def test_invalid_json_text(self):
        raw = FakeRaw("not-json")
        assert SchemaValidator.is_valid_json(raw, USER_SCHEMA) is False

    def test_raw_dict_input(self):
        data = {"id": 1, "name": "alice"}
        assert SchemaValidator.is_valid_json(data, USER_SCHEMA) is True

    def test_min_length_enforced(self):
        raw = FakeRaw(json.dumps({"id": 1, "name": ""}))
        assert SchemaValidator.is_valid_json(raw, USER_SCHEMA) is False