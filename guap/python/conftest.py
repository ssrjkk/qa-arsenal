import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).parent


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "critical: critical path tests")
    config.addinivalue_line("markers", "negative: negative tests")
    config.addinivalue_line("markers", "ui: UI tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "slow: slow running tests")


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environment: local, dev, staging, prod"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser for UI tests: chrome, firefox, edge"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode"
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "ui_tests" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        if "api_tests" in str(item.fspath):
            item.add_marker(pytest.mark.api)


@pytest.fixture(scope="session")
def project_root():
    return ROOT_DIR


@pytest.fixture(scope="session")
def test_data_dir():
    return ROOT_DIR / "tests_data"