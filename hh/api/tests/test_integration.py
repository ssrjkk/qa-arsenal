import allure
import pytest

from api.areas_api import AreasApi
from api.dictionaries_api import DictionariesApi
from api.vacancies_api import VacanciesApi
from validators.response_validator import ResponseValidator


@allure.feature("Интеграционные тесты")
@allure.story("Полный флоу поиска")
class TestSearchFlow:
    @pytest.mark.integration
    @pytest.mark.smoke
    @allure.title("Поиск вакансии и получение ее деталей")
    def test_search_then_get_detail(
        self,
        vacancies_api: VacanciesApi,
    ):
        search_response = vacancies_api.search(
            text="QA automation",
            area="2",
            per_page=5,
        )
        ResponseValidator(search_response).status(200)

        items = search_response.json()["items"]
        assert len(items) > 0, "Нет вакансий для теста"

        vacancy_id = items[0]["id"]
        detail_response = vacancies_api.get_by_id(vacancy_id)

        ResponseValidator(detail_response).status(200).key_equals(
            "id", vacancy_id
        ).raise_if_errors()

    @pytest.mark.integration
    @allure.title("Данные регионов и вакансий согласованы")
    def test_area_id_consistent(
        self,
        areas_api: AreasApi,
        vacancies_api: VacanciesApi,
    ):
        areas_response = areas_api.get_all()
        ResponseValidator(areas_response).status(200)

        areas = areas_response.json()
        russia = next((a for a in areas if "Россия" in a["name"]), None)
        assert russia is not None, "Россия не найдена"

        spb = next((a for a in russia["areas"] if a["id"] == "2"), None)
        assert spb is not None, "СПб не найден"

        vacancy_response = vacancies_api.search(
            text="tester",
            area=spb["id"],
            per_page=3,
        )

        ResponseValidator(vacancy_response).status(200).json_path("items").raise_if_errors()

    @pytest.mark.integration
    @allure.title("Фильтр опыта из справочника в поиске вакансий")
    def test_experience_filter_from_dict(
        self,
        dictionaries_api: DictionariesApi,
        vacancies_api: VacanciesApi,
    ):
        dict_response = dictionaries_api.get_all()
        ResponseValidator(dict_response).status(200)

        experience_ids = [e["id"] for e in dict_response.json()["experience"]]
        assert len(experience_ids) > 0, "Нет значений опыта"

        exp_id = experience_ids[0]
        vacancy_response = vacancies_api.search(
            text="QA",
            experience=exp_id,
            per_page=5,
        )

        ResponseValidator(vacancy_response).status(200).has_key("items").raise_if_errors()


@allure.feature("Интеграционные тесты")
@allure.story("Взаимосвязь справочников")
class TestDictionariesIntegration:
    @pytest.mark.integration
    @allure.title("Значения справочников применимы в фильтрах")
    def test_filter_combinations(
        self,
        dictionaries_api: DictionariesApi,
        vacancies_api: VacanciesApi,
    ):
        dict_response = dictionaries_api.get_all()
        data = dict_response.json()

        experience_ids = [e["id"] for e in data["experience"]]
        employment_ids = [e["id"] for e in data["employment"]]

        assert len(experience_ids) > 0
        assert len(employment_ids) > 0

        response = vacancies_api.search(
            text="developer",
            experience=experience_ids[0],
            employment=employment_ids[0],
            per_page=5,
        )

        ResponseValidator(response).status(200).json_path("items").raise_if_errors()
