import logging
import os
from typing import Any, Generator

import pytest

from api.areas_api import AreasApi
from api.dictionaries_api import DictionariesApi
from api.vacancies_api import VacanciesApi
from core.config import Config, get_config
from core.http_client import HTTPClient
from fixtures.data_fixtures import load_test_data

logging.basicConfig(
    level=logging.INFO if os.getenv("CI") else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def config() -> Config:
    return get_config()


@pytest.fixture(scope="session")
def http_client(config: Config) -> Generator[HTTPClient, None, None]:
    client = HTTPClient(
        base_url=config.base_url,
        timeout=config.timeout,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def vacancies_api(http_client: HTTPClient) -> VacanciesApi:
    return VacanciesApi(http_client)


@pytest.fixture(scope="session")
def areas_api(http_client: HTTPClient) -> AreasApi:
    return AreasApi(http_client)


@pytest.fixture(scope="session")
def dictionaries_api(http_client: HTTPClient) -> DictionariesApi:
    return DictionariesApi(http_client)


@pytest.fixture(scope="session")
def test_data() -> dict[str, Any]:
    return load_test_data()


@pytest.fixture(scope="session")
def valid_search_queries(test_data: dict[str, Any]) -> list[str]:
    return list(test_data["search_queries"]["valid"])


@pytest.fixture(scope="session")
def known_areas(test_data: dict[str, Any]) -> dict[str, str]:
    return dict(test_data["areas"])
