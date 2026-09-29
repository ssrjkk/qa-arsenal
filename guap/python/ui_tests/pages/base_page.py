from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class BasePage:
    TIMEOUT = 10

    def __init__(self, driver, timeout: int = None):
        self.driver = driver
        self.timeout = timeout or self.TIMEOUT
        self.wait = WebDriverWait(driver, self.timeout)

    def open(self, url: str) -> None:
        self.driver.get(url)
        self.wait_for_page_load()

    def wait_for_page_load(self, timeout: int = None) -> None:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def find(self, locator: tuple, timeout: int = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator: tuple, timeout: int = None) -> List[WebElement]:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def find_visible(self, locator: tuple, timeout: int = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: tuple, timeout: int = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator: tuple, timeout: int = None) -> None:
        element = self.find_clickable(locator, timeout)
        element.click()

    def type_text(self, locator: tuple, text: str, clear_first: bool = True) -> None:
        element = self.find_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple, timeout: int = None) -> str:
        return self.find_visible(locator, timeout).text

    def get_attribute(self, locator: tuple, attr: str, timeout: int = None) -> Optional[str]:
        return self.find(locator, timeout).get_attribute(attr)

    def is_visible(self, locator: tuple, timeout: int = None) -> bool:
        try:
            self.find_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def is_present(self, locator: tuple, timeout: int = None) -> bool:
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    def wait_until_text_in_element(self, locator: tuple, text: str, timeout: int = None) -> bool:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.text_to_be_present_in_element(locator, text))

    def wait_until_url_contains(self, text: str, timeout: int = None) -> bool:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.url_contains(text))

    def wait_until_url_matches(self, pattern: str, timeout: int = None) -> bool:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.url_matches(pattern))

    def scroll_to_element(self, locator: tuple) -> None:
        element = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def get_title(self) -> str:
        return self.driver.title

    def get_page_title(self) -> str:
        return self.driver.title

    def get_url(self) -> str:
        return self.driver.current_url

    def get_page_source(self) -> str:
        return self.driver.page_source

    def execute_script(self, script: str, *args):
        return self.driver.execute_script(script, *args)