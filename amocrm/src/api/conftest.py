"""API tests conftest."""

import pytest
from utils.api_client import HTTPClient


@pytest.fixture(scope="session")
def api_client() -> HTTPClient:
    """HTTP client fixture."""
    return HTTPClient()


@pytest.fixture(scope="function")
def test_user_data():
    """Generate random test user data."""
    import uuid

    unique = uuid.uuid4().hex[:8]
    return {"name": f"Test User {unique}", "email": f"test{unique}@example.com"}


@pytest.fixture(scope="function")
def created_user(api_client, test_user_data):
    """Create user and cleanup after test."""
    response = api_client.post("/api/users", json=test_user_data)

    if response.status_code == 201:
        user_id = response.json()["user"]["id"]
        yield user_id

        try:
            api_client.delete(f"/api/users/{user_id}")
        except Exception:
            pass
    else:
        yield None
