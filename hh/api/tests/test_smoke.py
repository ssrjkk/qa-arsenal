import allure
import pytest

from api.areas_api import AreasApi
from api.dictionaries_api import DictionariesApi
from api.vacancies_api import VacanciesApi
from validators.response_validator import ResponseValidator


@allure.feature("Smoke тесты")
@allure.story("Быстрая проверка API")
class TestSmoke:
    @pytest.mark.smoke
    @allure.title("Smoke: Vacancies API доступен")
    def test_vacancies_api_available(
        self,
        vacancies_api: VacanciesApi,
    ):
        response = vacancies_api.search(text="test", per_page=1)

        ResponseValidator(response).status(200).has_key("items").raise_if_errors()

    @pytest.mark.smoke
    @allure.title("Smoke: Areas API доступен")
    def test_areas_api_available(
        self,
        areas_api: AreasApi,
    ):
        response = areas_api.get_all()

        ResponseValidator(response).status(200).raise_if_errors()

    @pytest.mark.smoke
    @allure.title("Smoke: Dictionaries API доступен")
    def test_dictionaries_api_available(
        self,
        dictionaries_api: DictionariesApi,
    ):
        response = dictionaries_api.get_all()

        ResponseValidator(response).status(200).raise_if_errors()
