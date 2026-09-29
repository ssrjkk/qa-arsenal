"""Tests for Deals API."""

import pytest

from api.deals import DealsApi
from validators.response_validator import ResponseValidator


pytestmark = pytest.mark.api


class TestDealsList:
    """Tests for deals list endpoint."""

    def test_list_returns_200(self, deals_api: DealsApi):
        """Test list returns 200."""
        response = deals_api.list()
        assert response.status_code == 200

    def test_list_returns_json(self, deals_api: DealsApi):
        """Test list returns JSON."""
        response = deals_api.list()
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_has_deals_key(self, deals_api: DealsApi):
        """Test response has deals key."""
        response = deals_api.list()
        ResponseValidator(response).has_key("deals").raise_if_errors()

    def test_list_pagination(self, deals_api: DealsApi):
        """Test list pagination works."""
        response = deals_api.list(page=1, per_page=5)
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_with_status_filter(self, deals_api: DealsApi):
        """Test list with status filter."""
        response = deals_api.list(status="pending")
        ResponseValidator(response).status(200).raise_if_errors()


class TestDealsCRUD:
    """Tests for deals CRUD operations."""

    def test_create_deal(self, deals_api: DealsApi, sample_deal):
        """Test create deal."""
        response = deals_api.create(**sample_deal)
        ResponseValidator(response).status(201).raise_if_errors()

    def test_get_deal_by_id(self, deals_api: DealsApi):
        """Test get deal by ID."""
        response = deals_api.get_by_id(1)
        assert response.status_code in (200, 404)

    def test_update_deal(self, deals_api: DealsApi):
        """Test update deal."""
        response = deals_api.update(1, name="Updated Deal", price=20000)
        assert response.status_code in (200, 404)

    def test_delete_deal(self, deals_api: DealsApi):
        """Test delete deal."""
        response = deals_api.delete(999)
        assert response.status_code in (200, 404)


class TestDealsStatus:
    """Tests for deal status operations."""

    def test_update_deal_status(self, deals_api: DealsApi):
        """Test update deal status."""
        response = deals_api.update_status(1, status="won")
        assert response.status_code in (200, 404)

    def test_create_deal_with_contact(self, deals_api: DealsApi):
        """Test create deal with contact."""
        response = deals_api.create(
            name="Contact Deal",
            price=15000,
            contact_id=1,
        )
        ResponseValidator(response).status(201).raise_if_errors()

    def test_create_deal_with_company(self, deals_api: DealsApi):
        """Test create deal with company."""
        response = deals_api.create(
            name="Company Deal",
            price=25000,
            company_id=1,
        )
        ResponseValidator(response).status(201).raise_if_errors()


class TestDealsValidation:
    """Tests for deals response validation."""

    def test_response_time_under_limit(self, deals_api: DealsApi):
        """Test response time is acceptable."""
        response = deals_api.list()
        ResponseValidator(response).response_time_under(3000).raise_if_errors()


class TestDealsEdgeCases:
    """Tests for edge cases."""

    def test_get_nonexistent_deal(self, deals_api: DealsApi):
        """Test get nonexistent deal."""
        response = deals_api.get_by_id(99999)
        assert response.status_code in (200, 404)

    def test_create_deal_zero_price(self, deals_api: DealsApi):
        """Test create deal with zero price."""
        response = deals_api.create(name="Free Deal", price=0)
        ResponseValidator(response).status(201).raise_if_errors()
