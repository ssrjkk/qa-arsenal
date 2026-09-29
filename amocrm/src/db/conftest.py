"""Database tests conftest."""

import pytest
from utils.db_client import DBClient
from utils.api_client import HTTPClient


@pytest.fixture(scope="session")
def db_client() -> DBClient:
    """Database client fixture."""
    return DBClient()


@pytest.fixture(scope="function")
def api_client() -> HTTPClient:
    """API client fixture."""
    return HTTPClient()


@pytest.fixture(scope="function")
def clean_test_user(db_client):
    """Create and cleanup test user."""
    user_id = None

    yield user_id

    if user_id:
        try:
            db_client.execute_write("DELETE FROM users WHERE id = %s", (user_id,))
        except Exception:
            pass
