"""Hermetic unit tests for pydantic models (no network)."""

import pytest
from pydantic import ValidationError

from models.company import Company
from models.contact import Contact, ContactCreate, ContactUpdate


class TestContact:
    def test_valid_contact(self):
        c = Contact(id=1, name="Alice", email="alice@example.com")
        assert c.id == 1
        assert c.name == "Alice"

    def test_email_optional(self):
        c = Contact(id=1, name="Bob")
        assert c.email is None

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            Contact(id=1, name="X", email="not-an-email")

    def test_negative_id_rejected_by_type(self):
        with pytest.raises(ValidationError):
            Contact(id="not-int", name="X")


class TestContactCreate:
    def test_valid(self):
        c = ContactCreate(name="Alice")
        assert c.name == "Alice"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            ContactCreate(name="")

    def test_missing_name_rejected(self):
        with pytest.raises(ValidationError):
            ContactCreate()


class TestContactUpdate:
    def test_all_optional(self):
        c = ContactUpdate()
        assert c.name is None and c.phone is None

    def test_partial_update(self):
        c = ContactUpdate(name="New")
        assert c.name == "New"
        assert c.phone is None


class TestCompany:
    def test_valid_company(self):
        company = Company(id=1, name="Acme")
        assert company.name == "Acme"

    def test_invalid_name_type(self):
        with pytest.raises(ValidationError):
            Company(id=1, name=123)