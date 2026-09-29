import allure
import pytest

from api.vacancies_api import VacanciesApi
from validators.response_validator import ResponseValidator


@allure.feature("Vacancies API")
@allure.story("Поиск вакансий")
class TestVacanciesSearch:
    @pytest.mark.api
    @pytest.mark.smoke
    @allure.title("Поиск возвращает 200 и непустой список")
    def test_search_returns_results(
        self,
        vacancies_api: VacanciesApi,
        test_data: dict,
    ):
        response = vacancies_api.search(
            text="QA engineer",
            area=test_data["areas"]["spb"],
            per_page=10,
        )

        ResponseValidator(response).status(200).json_path("items").json_path(
            "items", lambda x: len(x) > 0
        ).json_path("found", lambda x: x >= 0).raise_if_errors()

    @pytest.mark.api
    @allure.title("Структура вакансии содержит обязательные поля")
    def test_vacancy_item_structure(
        self,
        vacancies_api: VacanciesApi,
        test_data: dict,
    ):
        response = vacancies_api.search(
            text="QA engineer",
            per_page=5,
        )

        ResponseValidator(response).status(200)
        data = response.json()

        assert len(data["items"]) > 0, "Список вакансий пуст"
        item = data["items"][0]

        required_fields = ["id", "name", "employer", "area"]
        for field in required_fields:
            assert field in item, f"Поле '{field}' отсутствует в вакансии"

    @pytest.mark.api
    @pytest.mark.parametrize("per_page", [5, 10, 20])
    @allure.title("Параметр per_page ограничивает количество результатов")
    def test_per_page_param(
        self,
        vacancies_api: VacanciesApi,
        per_page: int,
    ):
        response = vacancies_api.search(
            text="developer",
            per_page=per_page,
        )

        ResponseValidator(response).status(200).json_path(
            "items", lambda x: len(x) <= per_page
        ).raise_if_errors()

    @pytest.mark.api
    @pytest.mark.parametrize(
        "city,area_id",
        [("spb", "2"), ("moscow", "1")],
    )
    @allure.title("Поиск по региону фильтрует результаты")
    def test_search_by_area(
        self,
        vacancies_api: VacanciesApi,
        city: str,
        area_id: str,
    ):
        response = vacancies_api.search(
            text="tester",
            area=area_id,
            per_page=5,
        )

        ResponseValidator(response).status(200).json_path("items").raise_if_errors()

    @pytest.mark.api
    @pytest.mark.parametrize(
        "query",
        [
            "QA engineer",
            "Python developer",
            "DevOps",
        ],
    )
    @allure.title("Различные поисковые запросы возвращают результаты")
    def test_various_search_queries(
        self,
        vacancies_api: VacanciesApi,
        query: str,
    ):
        response = vacancies_api.search(
            text=query,
            per_page=5,
        )

        ResponseValidator(response).status(200).has_key("items").raise_if_errors()


@allure.feature("Vacancies API")
@allure.story("Детали вакансии")
class TestVacancyDetail:
    @pytest.mark.api
    @pytest.mark.smoke
    @allure.title("Получение вакансии по ID возвращает корректные данные")
    def test_get_vacancy_by_id(
        self,
        vacancies_api: VacanciesApi,
    ):
        search_response = vacancies_api.search(text="QA", per_page=1)
        items = search_response.json()["items"]
        assert len(items) > 0, "Нет вакансий для теста"
        vacancy_id = items[0]["id"]

        response = vacancies_api.get_by_id(vacancy_id)

        ResponseValidator(response).status(200).has_keys(
            ["id", "name", "description", "employer"]
        ).key_equals("id", vacancy_id).raise_if_errors()

    @pytest.mark.api
    @allure.title("Несуществующая вакансия возвращает 404")
    def test_vacancy_not_found(
        self,
        vacancies_api: VacanciesApi,
    ):
        response = vacancies_api.get_by_id("000000000")

        ResponseValidator(response).status(404).raise_if_errors()


@allure.feature("Vacancies API")
@allure.story("Фильтры поиска")
class TestSearchFilters:
    @pytest.mark.api
    @pytest.mark.parametrize(
        "experience_id",
        [
            "noExperience",
            "between1And3",
            "between3And6",
        ],
    )
    @allure.title("Фильтр по опыту работы")
    def test_experience_filter(
        self,
        vacancies_api: VacanciesApi,
        experience_id: str,
    ):
        response = vacancies_api.search(
            text="developer",
            experience=experience_id,
            per_page=10,
        )

        ResponseValidator(response).status(200).json_path("items").raise_if_errors()

    @pytest.mark.api
    @allure.title("Фильтр по типу занятости")
    def test_employment_filter(
        self,
        vacancies_api: VacanciesApi,
    ):
        response = vacancies_api.search(
            text="developer",
            employment="full",
            per_page=10,
        )

        ResponseValidator(response).status(200).json_path("items").raise_if_errors()


@allure.feature("Vacancies API")
@allure.story("Производительность")
class TestVacanciesPerformance:
    @pytest.mark.api
    @allure.title("Время ответа поиска вакансий")
    def test_search_response_time(
        self,
        vacancies_api: VacanciesApi,
        test_data: dict,
    ):
        response = vacancies_api.search(text="developer", per_page=10)

        ResponseValidator(response).status(200).response_time_under(
            test_data["expected_response_times"]["vacancies_search"]
        ).raise_if_errors()
