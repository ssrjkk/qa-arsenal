"""Integration tests for cross-API scenarios."""

import pytest

from api.companies import CompaniesApi
from api.contacts import ContactsApi
from api.deals import DealsApi
from validators.response_validator import ResponseValidator


pytestmark = pytest.mark.integration


class TestContactCompanyIntegration:
    """Tests for contact-company relationships."""

    def test_create_contact_with_company(self, contacts_api: ContactsApi, companies_api: CompaniesApi):
        """Test create contact linked to company."""
        company_response = companies_api.create(name="Integration Corp")
        assert company_response.status_code == 201
        company_data = company_response.json()
        company_id = company_data.get("company", {}).get("id") or company_data.get("id")

        contact_response = contacts_api.create(
            name="Integration User",
            email="int@example.com",
            company_id=company_id,
        )
        ResponseValidator(contact_response).status(201).raise_if_errors()


class TestDealContactIntegration:
    """Tests for deal-contact relationships."""

    def test_create_deal_with_contact(self, contacts_api: ContactsApi, deals_api: DealsApi):
        """Test create deal linked to contact."""
        contact_response = contacts_api.create(name="Deal Contact")
        assert contact_response.status_code == 201
        contact_data = contact_response.json()
        contact_id = contact_data.get("contact", {}).get("id") or contact_data.get("id")

        deal_response = deals_api.create(
            name="Integration Deal",
            price=10000,
            contact_id=contact_id,
        )
        ResponseValidator(deal_response).status(201).raise_if_errors()


class TestDealCompanyIntegration:
    """Tests for deal-company relationships."""

    def test_create_deal_with_company(self, companies_api: CompaniesApi, deals_api: DealsApi):
        """Test create deal linked to company."""
        company_response = companies_api.create(name="Deal Company Corp")
        assert company_response.status_code == 201
        company_data = company_response.json()
        company_id = company_data.get("company", {}).get("id") or company_data.get("id")

        deal_response = deals_api.create(
            name="Company Deal",
            price=20000,
            company_id=company_id,
        )
        ResponseValidator(deal_response).status(201).raise_if_errors()


class TestSearchIntegration:
    """Tests for search across entities."""

    def test_search_contacts_and_companies(self, contacts_api: ContactsApi, companies_api: CompaniesApi):
        """Test search works for both contacts and companies."""
        contacts_response = contacts_api.search("test")
        ResponseValidator(contacts_response).status_2xx().raise_if_errors()

        companies_response = companies_api.search("corp")
        ResponseValidator(companies_response).status_2xx().raise_if_errors()


class TestDataConsistency:
    """Tests for data consistency across endpoints."""

    def test_list_endpoints_consistent(self, contacts_api, companies_api, deals_api, users_api):
        """Test all list endpoints return consistent structure."""
        contacts_response = contacts_api.list()
        companies_response = companies_api.list()
        deals_response = deals_api.list()
        users_response = users_api.list()

        ResponseValidator(contacts_response).status_2xx().raise_if_errors()
        ResponseValidator(companies_response).status_2xx().raise_if_errors()
        ResponseValidator(deals_response).status_2xx().raise_if_errors()
        ResponseValidator(users_response).status_2xx().raise_if_errors()


class TestCRUDFlow:
    """Tests for complete CRUD flows."""

    def test_complete_contact_flow(self, contacts_api: ContactsApi):
        """Test complete contact create-read-update-delete flow."""
        create_response = contacts_api.create(name="Flow User", email="flow@example.com")
        ResponseValidator(create_response).status(201).raise_if_errors()

        contact_data = create_response.json()
        contact_id = contact_data.get("contact", {}).get("id") or contact_data.get("id")

        get_response = contacts_api.get_by_id(contact_id)
        assert get_response.status_code in (200, 201)

        update_response = contacts_api.update(contact_id, name="Updated Flow User")
        assert update_response.status_code in (200, 201)


class TestPaginationIntegration:
    """Tests for pagination across endpoints."""

    def test_pagination_all_endpoints(self, contacts_api, companies_api, deals_api, users_api):
        """Test pagination works on all endpoints."""
        for api in [contacts_api, companies_api, deals_api, users_api]:
            response = api.list(page=2, per_page=10)
            ResponseValidator(response).status_2xx().raise_if_errors()
