"""Hermetic unit tests for User models (no network)."""

import pytest
from pydantic import ValidationError

from models.user import User, UserCreate, UserUpdate


class TestUser:
    def test_valid_user(self):
        u = User(id=1, name="Alice", email="alice@example.com")
        assert u.email == "alice@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            User(id=1, name="X", email="nope")

    def test_missing_email_rejected(self):
        with pytest.raises(ValidationError):
            User(id=1, name="X")


class TestUserCreate:
    def test_valid(self):
        u = UserCreate(name="Bob", email="bob@example.com")
        assert u.name == "Bob"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(name="", email="b@example.com")

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(name="Bob", email="bad")


class TestUserUpdate:
    def test_all_optional(self):
        assert UserUpdate().model_dump(exclude_none=True) == {}

    def test_partial(self):
        u = UserUpdate(name="New Name")
        assert u.name == "New Name"
        assert u.email is None

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(email="bad")