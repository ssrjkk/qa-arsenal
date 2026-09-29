"""API tests conftest - совместимость."""

import sys
from pathlib import Path

# Добавить корень проекта в путь для импорта из src/
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from pipelines.api.utils.http_client import AmoCRMClient
from core.config import get_settings


def pytest_configure(config):
    config.addinivalue_line("markers", "api: API pipeline tests")
    config.addinivalue_line("markers", "contract: Contract validation tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")


@pytest.fixture(scope="session")
def api_client() -> AmoCRMClient:
    token = get_settings().amocrm_long_token
    return AmoCRMClient() if token else AmoCRMClient(long_token="")


@pytest.fixture(scope="session")
def api_token(api_client):
    if not api_client.token:
        pytest.skip("No LONG_TOKEN configured")
    return api_client.token


@pytest.fixture(scope="session")
def authenticated_client(api_client):
    if not api_client.token:
        pytest.skip("No LONG_TOKEN configured")
    return api_client


@pytest.fixture(scope="function")
def test_contact(api_client):
    resp = api_client.create_contact({"name": "Test Contact"})
    if resp.status_code != 200:
        yield None
    else:
        contact_id = resp.json()["_embedded"]["contacts"][0]["id"]
        yield contact_id
        try:
            api_client.delete_contact(contact_id)
        except Exception:
            pass


@pytest.fixture(scope="session")
def api_base_url():
    from core.config import get_amocrm_api_url

    return get_amocrm_api_url()


@pytest.fixture(scope="session")
def test_users():
    return {
        "admin": {"email": "admin@test.com", "password": "Admin123!"},
        "user": {"email": "user@test.com", "password": "User123!"},
    }
