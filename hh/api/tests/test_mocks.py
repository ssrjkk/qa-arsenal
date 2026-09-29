"""
Тесты с HTTP моками для демонстрации навыков мокирования.

Использует библиотеку responses - более профессионально для API фреймворка.
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
from validators.response_validator import ResponseValidator


@pytest.fixture
def http_client_mock() -> HTTPClient:
    """HTTPClient без retry для тестов с моками"""
    client = HTTPClient(
        base_url="https://api.hh.ru",
        timeout=30,
        skip_throttle=True,
    )
    client.session.mount("https://", HTTPAdapter(max_retries=Retry(total=0)))
    return client


@allure.feature("Vacancies API")
@allure.story("Поиск вакансий")
class TestVacanciesSearchMocked:
    @responses.activate
    @allure.title("Поиск возвращает пустой список когда нет результатов")
    def test_search_returns_empty_list(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [], "found": 0, "pages": 0, "per_page": 10, "page": 0},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        with allure.step("Отправляем запрос поиска с несуществующим текстом"):
            response = api.search(text="xyznonexistent123")

        with allure.step("Проверяем статус ответа"):
            assert response.status_code == 200

        data = response.json()
        assert data["found"] == 0
        assert len(data["items"]) == 0

    @responses.activate
    @allure.title("Поиск возвращает вакансии с правильной структурой")
    def test_search_returns_vacancies(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={
                "items": [
                    {
                        "id": "12345",
                        "name": "QA Engineer",
                        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                        "area": {"id": "1", "name": "Москва"},
                        "employer": {"id": "1455", "name": "HeadHunter"},
                        "experience": {"id": "between1And3", "name": "От 1 до 3 лет"},
                        "employment": {"id": "full", "name": "Полная занятость"},
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
        response = api.search(text="QA", area="1", per_page=10)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "QA Engineer"

    @responses.activate
    @allure.title("Поиск с фильтрами передает параметры в URL")
    def test_search_with_filters(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [], "found": 0, "pages": 0},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        api.search(text="Python", area="1", per_page=20, experience="between1And3")

        request = responses.calls[0].request
        assert "text=Python" in request.url
        assert "area=1" in request.url
        assert "per_page=20" in request.url
        assert "experience=between1And3" in request.url

    @responses.activate
    @allure.title("Поиск с параметром зарплаты")
    def test_search_with_salary(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [], "found": 0, "pages": 0},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        api.search(text="Developer", salary=100000, currency="RUR")

        request = responses.calls[0].request
        assert "salary=100000" in request.url
        assert "currency=RUR" in request.url

    @responses.activate
    @allure.title("Пагинация работает корректно")
    def test_pagination(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [], "found": 100, "pages": 10, "page": 2, "per_page": 10},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="QA", page=2, per_page=10)

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 10


@allure.feature("Vacancies API")
@allure.story("Детали вакансии")
class TestVacancyDetailMocked:
    @responses.activate
    @allure.title("Получение вакансии по ID возвращает корректные данные")
    def test_get_vacancy_by_id(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies/12345",
            json={
                "id": "12345",
                "name": "Senior Python Developer",
                "description": "Job description here",
                "salary": {"from": 200000, "to": 300000},
                "area": {"id": "1", "name": "Москва"},
            },
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.get_by_id("12345")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "12345"
        assert data["name"] == "Senior Python Developer"

    @responses.activate
    @allure.title("404 при получении несуществующей вакансии")
    def test_vacancy_detail_not_found(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies/999999999",
            json={"errors": [{"type": "not_found"}]},
            status=404,
        )

        api = VacanciesApi(http_client_mock)
        response = api.get_by_id("999999999")

        assert response.status_code == 404

    @responses.activate
    @allure.title("Похожие вакансии возвращают список")
    def test_similar_vacancies(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies/12345/similar_vacancies",
            json={"items": [{"id": "54321", "name": "Similar Job"}]},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.similar_vacancies("12345")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data


@allure.feature("Areas API")
@allure.story("Регионы")
class TestAreasMocked:
    @responses.activate
    @allure.title("Получение списка всех регионов")
    def test_get_all_areas(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/areas",
            json=[
                {"id": "1", "name": "Москва", "areas": []},
                {"id": "2", "name": "Санкт-Петербург", "areas": []},
            ],
            status=200,
        )

        api = AreasApi(http_client_mock)
        response = api.get_all()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Москва"

    @responses.activate
    @allure.title("Получение региона по ID")
    def test_get_area_by_id(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/areas/1",
            json={"id": "1", "name": "Москва", "areas": []},
            status=200,
        )

        api = AreasApi(http_client_mock)
        response = api.get_by_id("1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"

    @responses.activate
    @allure.title("Получение регионов (фильтр по типу)")
    def test_get_regions(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/areas",
            json=[{"id": "113", "name": "Россия", "areas": []}],
            status=200,
        )

        api = AreasApi(http_client_mock)
        response = api.get_regions()

        assert response.status_code == 200


@allure.feature("Dictionaries API")
@allure.story("Справочники")
class TestDictionariesMocked:
    @responses.activate
    @allure.title("Получение всех справочников")
    def test_get_all_dictionaries(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/dictionaries",
            json={
                "experience": [
                    {"id": "noExperience", "name": "Нет опыта"},
                    {"id": "between1And3", "name": "От 1 до 3 лет"},
                ],
                "employment": [
                    {"id": "full", "name": "Полная занятость"},
                    {"id": "part", "name": "Частичная занятость"},
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

    @responses.activate
    @allure.title("Получение конкретного справочника по имени")
    def test_get_dictionary_by_name(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/dictionaries/experience",
            json=[
                {"id": "noExperience", "name": "Нет опыта"},
                {"id": "between1And3", "name": "От 1 до 3 лет"},
            ],
            status=200,
        )

        api = DictionariesApi(http_client_mock)
        response = api.get_by_name("experience")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@allure.feature("Error Handling")
@allure.story("Обработка ошибок")
class TestErrorHandlingMocked:
    @responses.activate
    @allure.title("Обработка 500 ошибки сервера")
    def test_server_error_500(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"error": "Internal Server Error"},
            status=500,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        assert response.status_code == 500

    @responses.activate
    @allure.title("Обработка 429 Too Many Requests")
    def test_rate_limited_429(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"error": "Too Many Requests"},
            status=429,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        assert response.status_code == 429

    @responses.activate
    @allure.title("Обработка 403 Forbidden")
    def test_forbidden_403(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"errors": [{"type": "forbidden"}]},
            status=403,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        assert response.status_code == 403

    @responses.activate
    @allure.title("Обработка 400 Bad Request")
    def test_bad_request_400(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"errors": [{"type": "bad_argument", "value": "invalid"}]},
            status=400,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        assert response.status_code == 400


@allure.feature("Response Validator")
@allure.story("Валидация ответов")
class TestResponseValidatorMocked:
    @responses.activate
    @allure.title("Валидатор проверяет статус код")
    def test_validator_status_check(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [], "found": 0},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        ResponseValidator(response).status(200).raise_if_errors()

    @responses.activate
    @allure.title("Валидатор проверяет наличие ключей")
    def test_validator_has_keys(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [], "found": 0, "pages": 0},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        ResponseValidator(response).has_keys(["items", "found", "pages"]).raise_if_errors()

    @responses.activate
    @allure.title("Валидатор проверяет json_path")
    def test_validator_json_path(self, http_client_mock: HTTPClient) -> None:
        responses.add(
            responses.GET,
            "https://api.hh.ru/vacancies",
            json={"items": [{"id": "1"}], "found": 1},
            status=200,
        )

        api = VacanciesApi(http_client_mock)
        response = api.search(text="test")

        ResponseValidator(response).json_path("items", lambda x: len(x) > 0).raise_if_errors()
