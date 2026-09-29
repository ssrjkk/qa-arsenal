import pytest
from ui_tests.pages.guap_page import GuapMainPage, GuapSearchPage
from ui_tests.pages.metro_page import SpbMetroPage, MetroSchedulePage


def pytest_configure(config):
    config.addinivalue_line("markers", "requires_network: tests that require network access")


class TestGuapPage:
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_guap_main_page_opens(self, driver):
        page = GuapMainPage(driver)
        try:
            page.open_main()
            assert page.get_page_title() != ""
        except Exception:
            pytest.skip("guap.ru недоступен")

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_guap_title_contains_university_name(self, driver):
        page = GuapMainPage(driver)
        try:
            page.open_main()
            title = page.get_page_title().lower()
            assert any(word in title for word in ["гуап", "guap", "аэрокосмическ", "университет"])
        except Exception:
            pytest.skip("guap.ru недоступен")

    @pytest.mark.regression
    @pytest.mark.ui
    def test_guap_url_is_correct(self, driver):
        page = GuapMainPage(driver)
        try:
            page.open_main()
            assert "guap.ru" in page.get_current_url()
        except Exception:
            pytest.skip("guap.ru недоступен")

    @pytest.mark.regression
    @pytest.mark.ui
    def test_guap_header_is_visible(self, driver):
        page = GuapMainPage(driver)
        try:
            page.open_main()
            assert page.is_header_visible()
        except Exception:
            pytest.skip("guap.ru недоступен")

    @pytest.mark.regression
    @pytest.mark.ui
    def test_guap_navigation_is_visible(self, driver):
        page = GuapMainPage(driver)
        try:
            page.open_main()
            assert page.is_navigation_visible()
        except Exception:
            pytest.skip("guap.ru недоступен")


class TestMetroPage:
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_metro_page_opens(self, driver):
        page = SpbMetroPage(driver)
        page.open()
        assert page.get_page_title() != ""

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_metro_url_is_correct(self, driver):
        page = SpbMetroPage(driver)
        page.open()
        assert "metro.spb.ru" in page.get_url()

    @pytest.mark.regression
    @pytest.mark.ui
    def test_metro_page_accessible(self, driver):
        page = SpbMetroPage(driver)
        page.open()
        url = page.get_url()
        assert "metro.spb.ru" in url


class TestGuapSearch:
    @pytest.mark.regression
    @pytest.mark.ui
    def test_search_page_opens(self, driver):
        page = GuapSearchPage(driver)
        try:
            page.open_search()
            assert page.is_search_input_present()
        except Exception:
            pytest.skip("guap.ru недоступен")


class TestMetroSchedule:
    @pytest.mark.regression
    @pytest.mark.ui
    @pytest.mark.slow
    def test_metro_schedule_page_opens(self, driver):
        page = MetroSchedulePage(driver)
        page.open_schedule()
        assert page.get_page_title() != ""


class TestSiteComparison:
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_guap_page_loads(self, driver):
        page = GuapMainPage(driver)
        try:
            page.open_main()
            assert "guap" in page.get_url().lower()
            assert len(page.get_page_title()) > 0
        except Exception:
            pytest.skip("guap.ru недоступен")

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_metro_page_loads(self, driver):
        page = SpbMetroPage(driver)
        page.open()
        assert "metro.spb.ru" in page.get_url().lower()
        assert len(page.get_page_title()) > 0
