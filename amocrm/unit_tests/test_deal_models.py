"""Hermetic unit tests for Deal models (no network)."""

import pytest
from pydantic import ValidationError

from models.deal import Deal, DealCreate, DealUpdate


class TestDeal:
    def test_valid_deal(self):
        d = Deal(id=1, name="Big deal", price=100.0)
        assert d.id == 1
        assert d.status == "pending"

    def test_default_status(self):
        d = Deal(id=2, name="X", price=0.0)
        assert d.status == "pending"

    def test_invalid_price_type(self):
        with pytest.raises(ValidationError):
            Deal(id=1, name="X", price="not-number")

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            Deal(id=1, price=1.0)  # missing name


class TestDealCreate:
    def test_valid(self):
        d = DealCreate(name="Deal", price=50.0)
        assert d.name == "Deal"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            DealCreate(name="", price=1.0)

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            DealCreate(name="Deal", price=-1.0)

    def test_zero_price_allowed(self):
        d = DealCreate(name="Free", price=0.0)
        assert d.price == 0.0


class TestDealUpdate:
    def test_all_optional(self):
        assert DealUpdate().model_dump(exclude_none=True) == {}

    def test_partial(self):
        d = DealUpdate(name="New", status="won")
        assert d.name == "New"
        assert d.status == "won"

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            DealUpdate(price=-5.0)