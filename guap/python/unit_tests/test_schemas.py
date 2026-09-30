"""Hermetic unit tests for the schema validation layer (no network)."""

import pytest

from api_client.schemas import (
    FieldSchema,
    ResponseValidator,
    Schema,
    ValidationError,
    validate_field,
    validate_length,
    validate_object,
    validate_pattern,
    validate_type,
)


class TestValidateType:
    def test_valid_type_passes(self):
        validate_type(42, int, "id")

    def test_none_passes(self):
        validate_type(None, int, "id")

    def test_wrong_type_raises(self):
        with pytest.raises(ValidationError):
            validate_type("not-an-int", int, "id")


class TestValidatePattern:
    def test_matching_pattern_passes(self):
        validate_pattern("user@example.com", r"^[\w\.-]+@[\w\.-]+\.\w+$", "email")

    def test_bad_pattern_raises(self):
        with pytest.raises(ValidationError):
            validate_pattern("not-an-email", r"^[\w\.-]+@[\w\.-]+\.\w+$", "email")

    def test_empty_value_skips_check(self):
        validate_pattern("", r"^.+$", "name")


class TestValidateLength:
    def test_within_bounds_passes(self):
        validate_length("abc", 1, 5, "name")

    def test_below_min_raises(self):
        with pytest.raises(ValidationError):
            validate_length("", 1, None, "name")

    def test_above_max_raises(self):
        with pytest.raises(ValidationError):
            validate_length("abcdef", None, 3, "name")


class TestValidateField:
    def test_required_missing_raises(self):
        with pytest.raises(ValidationError):
            validate_field(None, FieldSchema("id", required=True), "id")

    def test_optional_none_passes(self):
        validate_field(None, FieldSchema("note", required=False), "note")

    def test_items_schema_applies_to_lists(self):
        schema = FieldSchema("items", items_schema=FieldSchema("n", type=int))
        validate_field([1, 2, 3], schema, "items")
        with pytest.raises(ValidationError):
            validate_field([1, "two"], schema, "items")


class TestValidateObject:
    def test_non_dict_returns_error(self):
        assert validate_object([], Schema([])) == ["Expected object, got list"]

    def test_collects_all_errors(self):
        errors = validate_object(
            {"id": "wrong", "name": ""},
            Schema([FieldSchema("id", type=int), FieldSchema("name", type=str, min_length=1)]),
        )
        assert len(errors) == 2


class TestResponseValidator:
    def test_valid_user_passes(self):
        user = {
            "id": 1,
            "name": "Alice",
            "username": "alice",
            "email": "alice@example.com",
            "phone": "123",
            "website": "alice.dev",
        }
        assert ResponseValidator.validate_user(user) == []

    def test_invalid_user_collects_errors(self):
        user = {"id": "x", "name": "", "email": "bad"}
        errors = ResponseValidator.validate_user(user)
        assert any("id" in e for e in errors)
        assert any("name" in e for e in errors)
        assert any("email" in e for e in errors)

    def test_valid_post_passes(self):
        post = {"id": 1, "userId": 1, "title": "t", "body": "b"}
        assert ResponseValidator.validate_post(post) == []

    def test_valid_todo_passes(self):
        todo = {"id": 1, "userId": 1, "title": "t", "completed": True}
        assert ResponseValidator.validate_todo(todo) == []

    def test_user_list_validates_each_item(self):
        users = [
            {"id": 1, "name": "a", "username": "a", "email": "a@b.c", "phone": "", "website": ""},
            {"id": 2, "name": "", "username": "", "email": "", "phone": "", "website": ""},
        ]
        assert len(ResponseValidator.validate_user_list(users)) == 2