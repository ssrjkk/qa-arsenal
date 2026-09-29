import re
import pytest
from playwright.sync_api import Page, expect


pytestmark = [pytest.mark.ui, pytest.mark.critical]


class TestCriticalUI:
    def test_login_page_loads(self, page: Page, ui_base_url: str):
        page.goto(ui_base_url)
        expect(page).to_have_url(re.compile(r".*"))

    def test_login_form_visible(self, page: Page, ui_base_url: str):
        page.goto(ui_base_url)
        expect(page.locator('input[name="LOGIN"]')).to_be_visible()

    def test_main_page_loads(self, page: Page, ui_base_url: str):
        page.goto(ui_base_url)
        expect(page).to_have_url(re.compile(r".*"))

    def test_contacts_list_page(self, page: Page, ui_base_url: str):
        page.goto(f"{ui_base_url}/contacts")
        expect(page).to_have_url(re.compile(r".*"))

    def test_leads_list_page(self, page: Page, ui_base_url: str):
        page.goto(f"{ui_base_url}/leads")
        expect(page).to_have_url(re.compile(r".*"))

    def test_companies_list_page(self, page: Page, ui_base_url: str):
        page.goto(f"{ui_base_url}/companies")
        expect(page).to_have_url(re.compile(r".*"))

    def test_tasks_page(self, page: Page, ui_base_url: str):
        page.goto(f"{ui_base_url}/tasks")
        expect(page).to_have_url(re.compile(r".*"))

    def test_no_horizontal_scroll(self, page: Page, ui_base_url: str):
        page.goto(ui_base_url)
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        assert scroll_width <= client_width

    def test_page_load_performance(self, page: Page, ui_base_url: str):
        import time

        start = time.time()
        page.goto(ui_base_url)
        load_time = (time.time() - start) * 1000
        assert load_time < 10000, f"Page too slow: {load_time}ms"


@pytest.mark.skip(reason="Requires real browser binary")
class TestCrossBrowserUI:
    def test_all_browsers_login_page(self, ui_browser):
        pass
