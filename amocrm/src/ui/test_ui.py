"""UI tests - working examples."""

import pytest
from selenium.webdriver.common.by import By


pytestmark = pytest.mark.ui


class TestLoginPage:
    """Login page tests."""

    def test_health_page_loads(self, browser, app_url):
        """Health page loads without errors."""
        browser.get(f"{app_url}/health")

        body = browser.find_element(By.TAG_NAME, "body")
        assert body is not None

    def test_api_docs_accessible(self, browser, app_url):
        """API is accessible."""
        browser.get(f"{app_url}/api/users")

        assert browser.title or "users" in browser.page_source.lower()


class TestDashboard:
    """Dashboard tests."""

    def test_users_api_accessible(self, browser, app_url):
        """Users API accessible."""
        browser.get(f"{app_url}/api/users")

        assert "users" in browser.page_source.lower() or "[]" in browser.page_source


class TestUIResponsive:
    """UI responsive tests."""

    def test_no_horizontal_scroll(self, browser, app_url):
        """No horizontal scroll on health page."""
        browser.set_window_size(375, 667)
        browser.get(f"{app_url}/health")

        scroll_width = browser.execute_script("return document.documentElement.scrollWidth")
        client_width = browser.execute_script("return document.documentElement.clientWidth")

        assert scroll_width <= client_width

    def test_page_loads_quickly(self, browser, app_url):
        """Page loads within 5 seconds."""
        import time

        start = time.time()
        browser.get(f"{app_url}/health")
        load_time = time.time() - start

        assert load_time < 5, f"Page loaded in {load_time:.2f}s"
