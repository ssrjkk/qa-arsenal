"""Hermetic unit tests for ResponseValidator (fake responses, no network)."""

import json
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from validators.response_validator import ResponseValidator


class FakeResponse:
    def __init__(self, status_code=200, text="", json_data=None, elapsed_ms=10.0):
        self.status_code = status_code
        self.text = text
        self._json = json_data
        self.elapsed = SimpleNamespace(total_seconds=lambda: elapsed_ms / 1000.0)

    def json(self):
        if self._json is None:
            raise json.JSONDecodeError("no json", "doc", 0)
        return self._json


class Item(BaseModel):
    id: int
    name: str


def make(status_code=200, json_data=None, text="", elapsed_ms=10.0) -> ResponseValidator:
    return ResponseValidator(FakeResponse(status_code, text, json_data, elapsed_ms))


class TestStatus:
    def test_matching_status_no_error(self):
        assert make(status_code=200).status(200).raise_if_errors() is None

    def test_mismatched_status_records_error(self):
        v = make(status_code=404)
        v.status(200)
        with pytest.raises(AssertionError):
            v.raise_if_errors()

    def test_status_in_range(self):
        assert make(status_code=201).status_in([200, 201, 202]).raise_if_errors() is None

    def test_status_not_in_range_records_error(self):
        v = make(status_code=500)
        v.status_in([200, 201])
        with pytest.raises(AssertionError):
            v.raise_if_errors()


class TestJsonPath:
    def test_root_path(self):
        v = make(json_data={"a": 1})
        v.json_path("$", lambda d: d.get("a") == 1)
        assert not v._errors

    def test_nested_path(self):
        v = make(json_data={"items": [{"id": 1}]})
        v.json_path("items.0.id", lambda x: x == 1)
        assert not v._errors

    def test_missing_path_records_error(self):
        v = make(json_data={"a": 1})
        v.json_path("missing")
        with pytest.raises(AssertionError):
            v.raise_if_errors()

    def test_validator_failure_records_error(self):
        v = make(json_data={"items": [{"id": 1}]})
        v.json_path("items.0.id", lambda x: x == 99)
        with pytest.raises(AssertionError):
            v.raise_if_errors()


class TestKeys:
    def test_has_key(self):
        assert make(json_data={"id": 1}).has_key("id").raise_if_errors() is None

    def test_missing_key_records_error(self):
        v = make(json_data={"id": 1})
        v.has_key("name")
        with pytest.raises(AssertionError):
            v.raise_if_errors()

    def test_key_equals(self):
        assert make(json_data={"name": "qa"}).key_equals("name", "qa").raise_if_errors() is None

    def test_key_type(self):
        assert make(json_data={"id": 1}).key_type("id", int).raise_if_errors() is None

    def test_key_type_mismatch(self):
        v = make(json_data={"id": "not-int"})
        v.key_type("id", int)
        with pytest.raises(AssertionError):
            v.raise_if_errors()


class TestLists:
    def test_list_not_empty(self):
        assert make(json_data={"items": [1, 2]}).list_not_empty("items").raise_if_errors() is None

    def test_empty_list_records_error(self):
        v = make(json_data={"items": []})
        v.list_not_empty("items")
        with pytest.raises(AssertionError):
            v.raise_if_errors()

    def test_list_length(self):
        assert make(json_data={"items": [1, 2, 3]}).list_length("items", 3).raise_if_errors() is None

    def test_list_max_length(self):
        v = make(json_data={"items": [1, 2, 3, 4]})
        v.list_max_length("items", 3)
        with pytest.raises(AssertionError):
            v.raise_if_errors()


class TestResponseTime:
    def test_under_limit_passes(self):
        assert make(elapsed_ms=50).response_time_under(100).raise_if_errors() is None

    def test_over_limit_records_error(self):
        v = make(elapsed_ms=150)
        v.response_time_under(100)
        with pytest.raises(AssertionError):
            v.raise_if_errors()


class TestModel:
    def test_valid_model(self):
        v = make(json_data={"id": 1, "name": "x"})
        item = v.model(Item)
        assert isinstance(item, Item)
        assert item.id == 1

    def test_invalid_model_raises(self):
        v = make(json_data={"id": "x"})
        with pytest.raises(Exception):
            v.model(Item)


class TestBrokenJson:
    def test_bad_json_returns_empty_and_records_error(self):
        v = make(status_code=200, text="not-json")
        assert v.data == {}
        with pytest.raises(AssertionError):
            v.raise_if_errors()