from selenium.webdriver.common.by import By
from .base_page import BasePage


class SpbMetroPage(BasePage):
    URL = "https://www.metro.spb.ru"

    HEADER = (By.TAG_NAME, "header")
    NAVIGATION = (By.CSS_SELECTOR, "nav, .nav-menu, .main-menu")
    MAP_LINK = (By.PARTIAL_LINK_TEXT, "схем")
    NEWS_SECTION = (By.CSS_SELECTOR, ".news, [class*='news'], [id*='news']")
    FOOTER = (By.TAG_NAME, "footer")
    MAIN_CONTENT = (By.CSS_SELECTOR, "main, .main-content, .content")

    def open(self):
        super().open(self.URL)

    def is_page_loaded(self) -> bool:
        return self.is_visible(self.HEADER)

    def get_page_title(self) -> str:
        return self.get_title()

    def get_url(self) -> str:
        return self.driver.current_url

    def is_navigation_visible(self) -> bool:
        return self.is_visible(self.NAVIGATION)

    def is_news_section_visible(self) -> bool:
        return self.is_visible(self.NEWS_SECTION)

    def is_footer_visible(self) -> bool:
        return self.is_visible(self.FOOTER)

    def click_map_link(self):
        self.click(self.MAP_LINK)

    def get_main_content_text(self) -> str:
        return self.get_text(self.MAIN_CONTENT)


class MetroSchedulePage(BasePage):
    URL = "https://www.metro.spb.ru/metro/scheme"

    SCHEME_MAP = (By.ID, "scheme-map")
    STATIONS_LIST = (By.CSS_SELECTOR, ".stations, .stations-list")
    STATION_ITEM = (By.CSS_SELECTOR, ".station, .station-item")

    def open_schedule(self):
        self.open(self.URL)

    def is_scheme_visible(self) -> bool:
        return self.is_visible(self.SCHEME_MAP)

    def get_stations_count(self) -> int:
        return len(self.find_all(self.STATION_ITEM))

    def click_station(self, station_name: str):
        locator = (By.XPATH, f"//*[contains(text(), '{station_name}')]")
        self.click(locator)