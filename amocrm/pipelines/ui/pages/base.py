"""Advanced BasePage with wait helpers and error handling."""

import allure
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class BasePage:
    """Base page object with common functionality."""

    def __init__(self, page: Page):
        self.page = page
        self._default_timeout = 30000

    def goto(self, path: str = "", timeout: int = 30000):
        """Navigate to URL."""
        from config.settings import BASE_URL

        url = f"{BASE_URL}{path}"
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, timeout=timeout)
        return self

    def reload(self, timeout: int = 30000):
        """Reload current page."""
        self.page.reload(timeout=timeout)

    def click(self, selector: str, timeout: int = None):
        """Click element."""
        self.page.click(selector, timeout=timeout or self._default_timeout)

    def fill(self, selector: str, value: str, clear: bool = True):
        """Fill input field."""
        if clear:
            self.page.fill(selector, "")
        self.page.fill(selector, value)

    def select_option(self, selector: str, value: str):
        """Select option from dropdown."""
        self.page.select_option(selector, value)

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is visible."""
        try:
            return self.page.is_visible(selector, timeout=timeout)
        except PlaywrightTimeoutError:
            return False

    def is_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """Check if element is hidden."""
        try:
            return self.page.is_hidden(selector, timeout=timeout)
        except PlaywrightTimeoutError:
            return True

    def wait_for_selector(self, selector: str, timeout: int = None):
        """Wait for selector to appear."""
        self.page.wait_for_selector(selector, timeout=timeout or self._default_timeout)

    def wait_for_url(self, pattern: str, timeout: int = None):
        """Wait for URL to match pattern."""
        self.page.wait_for_url(pattern, timeout=timeout or self._default_timeout)

    def wait_for_load_state(self, state: str = "load", timeout: int = None):
        """Wait for page load state."""
        self.page.wait_for_load_state(state, timeout=timeout or self._default_timeout)

    def get_text(self, selector: str) -> str:
        """Get text content."""
        return self.page.text_content(selector) or ""

    def get_attribute(self, selector: str, attr: str) -> Optional[str]:
        """Get element attribute."""
        return self.page.get_attribute(selector, attr)

    def count_elements(self, selector: str) -> int:
        """Count elements matching selector."""
        return self.page.locator(selector).count()

    def wait_until(self, condition: Callable[[], bool], timeout: int = 30000, poll_interval: int = 500) -> bool:
        """Wait until condition is true."""
        import time

        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                if condition():
                    return True
            except Exception:
                pass
            time.sleep(poll_interval / 1000)
        return False

    def screenshot(self, name: str = "screenshot", full_page: bool = False):
        """Take screenshot and attach to Allure."""
        path = f"reports/{name}.png"
        self.page.screenshot(path=path, full_page=full_page)
        allure.attach.file(path, name=name, attachment_type=allure.AttachmentType.PNG)

    def attach_page_source(self, name: str = "page_source"):
        """Attach page source to Allure."""
        allure.attach(self.page.content(), name=name, attachment_type=allure.AttachmentType.HTML)


class BaseElement:
    """Base element with common interactions."""

    def __init__(self, page: Page, selector: str, name: str = None):
        self.page = page
        self.selector = selector
        self.name = name or selector
        self.locator: Locator = page.locator(selector)

    def click(self, timeout: int = None):
        """Click element."""
        self.locator.click(timeout=timeout)
        logger.debug(f"Clicked: {self.name}")

    def double_click(self, timeout: int = None):
        """Double click element."""
        self.locator.dblclick(timeout=timeout)

    def hover(self, timeout: int = None):
        """Hover over element."""
        self.locator.hover(timeout=timeout)

    def fill(self, value: str, clear: bool = True):
        """Fill input."""
        if clear:
            self.locator.fill("")
        self.locator.fill(value)

    def select_option(self, value: str):
        """Select option."""
        self.locator.select_option(value)

    def is_visible(self, timeout: int = 5000) -> bool:
        """Check visibility."""
        try:
            return self.locator.is_visible(timeout=timeout)
        except PlaywrightTimeoutError:
            return False

    def is_enabled(self) -> bool:
        """Check if enabled."""
        return self.locator.is_enabled()

    def is_disabled(self) -> bool:
        """Check if disabled."""
        return not self.locator.is_enabled()

    def get_text(self) -> str:
        """Get text content."""
        return self.locator.text_content() or ""

    def get_attribute(self, attr: str) -> Optional[str]:
        """Get attribute."""
        return self.locator.get_attribute(attr)

    def wait_for(self, state: str = "visible", timeout: int = None):
        """Wait for state."""
        self.locator.wait_for(state=state, timeout=timeout)

    def should_be_visible(self, timeout: int = None):
        """Assert element is visible."""
        assert self.is_visible(timeout), f"Element {self.name} should be visible"

    def should_be_enabled(self):
        """Assert element is enabled."""
        assert self.is_enabled(), f"Element {self.name} should be enabled"


class BaseModal(BasePage):
    """Base modal dialog."""

    @property
    def modal_root(self):
        return '[role="dialog"], .modal, .popup'

    def is_open(self) -> bool:
        return self.is_visible(self.modal_root, timeout=3000)

    def close(self):
        """Close modal."""
        close_buttons = ['[aria-label="Close"]', ".modal-close", ".popup-close", "button.close"]
        for btn in close_buttons:
            if self.is_visible(btn, timeout=2000):
                self.click(btn)
                break

    def wait_for_open(self, timeout: int = None):
        self.wait_for_selector(self.modal_root, timeout)

    def wait_for_close(self, timeout: int = None):
        import time

        start = time.time()
        timeout_sec = (timeout or 10000) / 1000
        while time.time() - start < timeout_sec:
            if not self.is_open():
                return
            time.sleep(0.5)
        raise AssertionError("Modal should be closed")


class BaseForm(BasePage):
    """Base form with common operations."""

    def fill_field(self, field: str, value: str):
        """Fill form field."""
        self.fill(f'[name="{field}"], [id="{field}"], [data-testid="{field}"]', value)

    def fill_fields(self, data: dict):
        """Fill multiple fields."""
        for field, value in data.items():
            self.fill_field(field, value)

    def submit(self, selector: str = 'button[type="submit"]'):
        """Submit form."""
        self.click(selector)
        self.wait_for_load_state("networkidle")

    def get_error_message(self) -> str:
        """Get form error message."""
        error_selectors = [".error", ".invalid", '[role="alert"]', ".error-message"]
        for sel in error_selectors:
            if self.is_visible(sel):
                return self.get_text(sel)
        return ""
