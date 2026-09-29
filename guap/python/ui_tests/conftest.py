import logging
import sys
import pytest
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = Path("screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def get_chrome_options() -> Options:
    options = Options()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return options


def get_firefox_options() -> FirefoxOptions:
    options = FirefoxOptions()
    if config.HEADLESS:
        options.add_argument("--headless")
    options.add_argument(f"--width={config.WINDOW_WIDTH}")
    options.add_argument(f"--height={config.WINDOW_HEIGHT}")
    return options


def create_driver():
    if config.BROWSER.lower() == "chrome":
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
    elif config.BROWSER.lower() == "firefox":
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=get_firefox_options())
    else:
        raise ValueError(f"Unsupported browser: {config.BROWSER}")

    driver.implicitly_wait(0)
    driver.set_page_load_timeout(config.TIMEOUT_PAGE_LOAD)
    logger.info(f"Created {config.BROWSER} driver")
    return driver


@pytest.fixture(scope="session")
def browser_config():
    return {
        "browser": config.BROWSER,
        "headless": config.HEADLESS,
        "window_size": (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
        "timeouts": {
            "implicit": config.TIMEOUT_IMPLICIT,
            "explicit": config.TIMEOUT_EXPLICIT,
            "page_load": config.TIMEOUT_PAGE_LOAD
        }
    }


@pytest.fixture(scope="session")
def driver():
    driver = create_driver()
    yield driver
    driver.quit()
    logger.info("Quit driver")


@pytest.fixture(scope="session")
def wait(driver):
    return WebDriverWait(driver, config.TIMEOUT_EXPLICIT)


@pytest.fixture(scope="session")
def base_url():
    return config.BASE_URL


@pytest.fixture(scope="function")
def page(driver, wait):
    class PageWrapper:
        def __init__(self, driver, wait):
            self._driver = driver
            self._wait = wait

        def __getattr__(self, name):
            return getattr(self._driver, name)

        @property
        def wait(self):
            return self._wait

    return PageWrapper(driver, wait)


def take_screenshot(driver, name: str = None):
    if name is None:
        name = f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    driver.save_screenshot(str(filepath))
    logger.warning(f"Screenshot saved: {filepath}")
    return filepath


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            try:
                test_name = item.nodeid.replace("::", "_").replace("/", "_")
                take_screenshot(driver, test_name)
            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "critical: critical path tests")
    config.addinivalue_line("markers", "negative: negative tests")
    config.addinivalue_line("markers", "ui: UI tests")
    config.addinivalue_line("markers", "slow: slow running tests")


def pytest_runtest_logreport(report):
    if report.when == "call" and report.failed:
        logger.error(f"TEST FAILED: {report.nodeid}")
    elif report.when == "call" and report.passed:
        logger.info(f"TEST PASSED: {report.nodeid}")