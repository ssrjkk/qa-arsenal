"""
Contract tests for HH.ru API.

Validates API responses against expected schemas.
Uses JSON Schema validation for contract testing.
"""

import allure
import pytest
import responses
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.areas_api import AreasApi
from api.dictionaries_api import DictionariesApi
from api.vacancies_api import VacanciesApi
from core.http_client import HTTPClient
from validators.schema_validator import validate_schema


@pytest.fixture
def http_client_mock() -> HTTPClient:
    """HTTPClient without retry for contract tests"""
    client = HTTPClient(
        base_url="https://api.hh.ru",
        timeout=30,
        skip_throttle=True,
    )
    client.session.mount("https://", HTTPAdapter(max_retries=Retry(total=0)))
    return client


VACANCY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "area": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        },
    },
    "required": ["id", "name"],
}


SEARCH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": VACANCY_SCHEMA,
        },
        "found": {"type": "integer", "minimum": 0},
        "pages": {"type": "integer", "minimum": 0},
        "per_page": {"type": "integer", "minimum": 1},
        "page": {"type": "integer", "minimum": 0},
    },
    "required": ["items", "found", "pages"],
}


AREA_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "areas": {
            "type": "array",
            "items": {"$ref": "#/definitions/Area"},
        },
    },
    "required": ["id", "name"],
    "definitions": {
        "Area": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        }
    },
}


@allure.feature("Contract Testing")
@allure.story("Vacancies API Contract")
class TestVacanciesContract:
    @responses.activate
    @allure.title("Search response matches JSON schema")
    def test_search_response_schema(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={
                "items": [
                    {
                        "id": "12345",
                        "name": "QA Engineer",
                        "area": {"id": "1", "name": "Moscow"},
                    }
                ],
                "found": 1,
                "pages": 1,
                "per_page": 10,
                "page": 0,
            },
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="QA", per_page=1)

        assert response.status_code == 200
        data = response.json()

        errors = validate_schema(data, SEARCH_RESPONSE_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"

    @responses.activate
    @allure.title("Vacancy detail has required fields")
    def test_vacancy_detail_schema(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies/12345",
            json={
                "id": "12345",
                "name": "Senior Python Developer",
                "area": {"id": "1", "name": "Moscow"},
                "employer": {"id": "1455", "name": "Company"},
            },
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.get_by_id("12345")

        assert response.status_code == 200
        data = response.json()

        errors = validate_schema(data, VACANCY_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"


@allure.feature("Contract Testing")
@allure.story("Areas API Contract")
class TestAreasContract:
    @responses.activate
    @allure.title("Areas list response has correct structure")
    def test_areas_list_schema(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/areas",
            json=[
                {
                    "id": "1",
                    "name": "Moscow",
                    "areas": [
                        {"id": "2", "name": "Saint Petersburg"}
                    ],
                }
            ],
            status=200,
        )

        api = AreasApi(http_client_mock)
        response = api.get_all()

        assert response.status_code == 200
        data = response.json()

        # Validate first area
        errors = validate_schema(data[0], AREA_SCHEMA)
        assert not errors, f"Schema validation failed: {errors}"


@allure.feature("Contract Testing")
@allure.story("Dictionaries API Contract")
class TestDictionariesContract:
    @responses.activate
    @allure.title("Dictionaries response has required fields")
    def test_dictionaries_schema(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/dictionaries",
            json={
                "experience": [
                    {"id": "noExperience", "name": "No experience"},
                ],
                "employment": [
                    {"id": "full", "name": "Full time"},
                ],
            },
            status=200,
        )

        api = DictionariesApi(http_client_mock)
        response = api.get_all()

        assert response.status_code == 200
        data = response.json()

        assert "experience" in data
        assert "employment" in data
        assert isinstance(data["experience"], list)
        assert len(data["experience"]) > 0
