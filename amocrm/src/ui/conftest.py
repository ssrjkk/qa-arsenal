"""UI tests conftest."""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from core.config import get_settings


@pytest.fixture(scope="session")
def browser():
    """Selenium WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="session")
def app_url():
    """Application URL."""
    return get_settings().app_url
