import logging
import sys
import pytest
import requests

from config.settings import config
from api_client.base import BaseApiClient

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def base_url():
    return config.BASE_URL


@pytest.fixture(scope="session")
def env():
    return config.ENV


@pytest.fixture(scope="session")
def http_session():
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "QA Test Framework"
    })
    logger.info("Created HTTP session")
    yield session
    session.close()
    logger.info("Closed HTTP session")


@pytest.fixture(scope="session")
def api_client(http_session):
    client = BaseApiClient(session=http_session)
    logger.info(f"Created API client for {config.BASE_URL}")
    yield client
    client.close()
    logger.info("Closed API client")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "critical: critical path tests")
    config.addinivalue_line("markers", "negative: negative tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "ui: UI tests")


def pytest_runtest_logreport(report):
    if report.when == "call" and report.failed:
        logger.error(f"TEST FAILED: {report.nodeid}")
    elif report.when == "call" and report.passed:
        logger.info(f"TEST PASSED: {report.nodeid}")
