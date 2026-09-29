import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _get_int(key: str, default: int = 0) -> int:
    return int(os.getenv(key, str(default)))


def _get_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


@dataclass
class Config:
    BASE_URL_API: str = _get_env("BASE_URL_API", "https://jsonplaceholder.typicode.com")
    BASE_URL_UI: str = _get_env("BASE_URL_UI", "https://guap.ru")
    ENV: str = _get_env("ENV", "local")
    BROWSER: str = _get_env("BROWSER", "chrome")

    TIMEOUT_IMPLICIT: int = _get_int("TIMEOUT_IMPLICIT", 5)
    TIMEOUT_EXPLICIT: int = _get_int("TIMEOUT_EXPLICIT", 10)
    TIMEOUT_PAGE_LOAD: int = _get_int("TIMEOUT_PAGE_LOAD", 30)

    HEADLESS: bool = _get_bool("HEADLESS", True)
    WINDOW_WIDTH: int = _get_int("WINDOW_WIDTH", 1920)
    WINDOW_HEIGHT: int = _get_int("WINDOW_HEIGHT", 1080)

    ALLURE_RESULTS_DIR: str = _get_env("ALLURE_RESULTS_DIR", "allure-results")
    ALLURE_REPORT_DIR: str = _get_env("ALLURE_REPORT_DIR", "allure-report")

    LOG_LEVEL: str = _get_env("LOG_LEVEL", "INFO")
    LOG_FILE: str = _get_env("LOG_FILE", "test.log")


config = Config()