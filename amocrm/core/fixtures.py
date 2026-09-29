"""Base pytest fixtures."""

import pytest
import allure

from core.config import get_settings
from core.logger import get_logger
from utils.api_client import HTTPClient
from utils.db_client import DBClient


@pytest.fixture(scope="session")
def config():
    """Get settings."""
    return get_settings()


@pytest.fixture(scope="session")
def logger():
    """Get logger."""
    return get_logger("tests")


@pytest.fixture(scope="session")
def api_client() -> HTTPClient:
    """HTTP API client."""
    return HTTPClient()


@pytest.fixture(scope="session")
def db_client() -> DBClient:
    """Database client."""
    return DBClient()


@pytest.fixture(scope="function")
def db_transaction(db_client):
    """Transaction fixture with rollback."""
    with db_client.connection() as conn:
        yield conn
        conn.rollback()


def attach_screenshot(name: str = "screenshot", page=None):
    """Attach screenshot to Allure."""
    try:
        if page and hasattr(page, "screenshot"):
            screenshot = page.screenshot()
            allure.attach(screenshot, name=name, attachment_type=allure.AttachmentType.PNG)
    except Exception:
        pass


def attach_log(name: str, content: str):
    """Attach log to Allure."""
    allure.attach(content, name=name, attachment_type=allure.AttachmentType.TEXT)


def pytest_configure(config):
    """Register markers."""
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "db: Database tests")
    config.addinivalue_line("markers", "ui: UI tests")
    config.addinivalue_line("markers", "kafka: Kafka tests")
    config.addinivalue_line("markers", "load: Load tests")
    config.addinivalue_line("markers", "k8s: K8s tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "critical: Critical tests")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot on failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Try to attach screenshot if available
        if hasattr(item, "funcargs"):
            page = item.funcargs.get("page")
            if page:
                attach_screenshot(f"{item.name}_failed", page)
