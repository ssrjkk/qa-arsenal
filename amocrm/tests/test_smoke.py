"""Smoke tests for quick validation."""

import pytest

from api.companies import CompaniesApi
from api.contacts import ContactsApi
from api.deals import DealsApi
from api.users import UsersApi
from core.http_client import HTTPClient
from validators.response_validator import ResponseValidator


pytestmark = pytest.mark.smoke


class TestHealthCheck:
    """Health check tests."""

    def test_health_endpoint(self, http_client: HTTPClient):
        """Test health endpoint returns 200."""
        response = http_client.get("/health")
        ResponseValidator(response).status(200).raise_if_errors()


class TestContactsSmoke:
    """Smoke tests for contacts."""

    def test_contacts_list_smoke(self, contacts_api: ContactsApi):
        """Test contacts list works."""
        response = contacts_api.list()
        ResponseValidator(response).status_2xx().raise_if_errors()

    def test_contacts_create_smoke(self, contacts_api: ContactsApi):
        """Test contacts create works."""
        response = contacts_api.create(name="Smoke Test Contact", email="smoke@test.com")
        ResponseValidator(response).status_2xx().raise_if_errors()


class TestCompaniesSmoke:
    """Smoke tests for companies."""

    def test_companies_list_smoke(self, companies_api: CompaniesApi):
        """Test companies list works."""
        response = companies_api.list()
        ResponseValidator(response).status_2xx().raise_if_errors()

    def test_companies_create_smoke(self, companies_api: CompaniesApi):
        """Test companies create works."""
        response = companies_api.create(name="Smoke Corp")
        ResponseValidator(response).status_2xx().raise_if_errors()


class TestDealsSmoke:
    """Smoke tests for deals."""

    def test_deals_list_smoke(self, deals_api: DealsApi):
        """Test deals list works."""
        response = deals_api.list()
        ResponseValidator(response).status_2xx().raise_if_errors()

    def test_deals_create_smoke(self, deals_api: DealsApi):
        """Test deals create works."""
        response = deals_api.create(name="Smoke Deal", price=1000)
        ResponseValidator(response).status_2xx().raise_if_errors()


class TestUsersSmoke:
    """Smoke tests for users."""

    def test_users_list_smoke(self, users_api: UsersApi):
        """Test users list works."""
        response = users_api.list()
        ResponseValidator(response).status_2xx().raise_if_errors()
