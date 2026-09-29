import allure
import pytest

from api.dictionaries_api import DictionariesApi
from validators.response_validator import ResponseValidator


@allure.feature("Dictionaries API")
@allure.story("Справочники")
class TestDictionaries:
    @pytest.mark.api
    @pytest.mark.smoke
    @allure.title("Справочники возвращают 200")
    def test_dictionaries_ok(
        self,
        dictionaries_api: DictionariesApi,
    ):
        response = dictionaries_api.get_all()

        ResponseValidator(response).status(200).has_keys(
            ["vacancy_type", "experience", "employment", "schedule"]
        ).raise_if_errors()

    @pytest.mark.api
    @allure.title("Значения опыта работы содержат id и name")
    def test_experience_structure(
        self,
        dictionaries_api: DictionariesApi,
    ):
        response = dictionaries_api.get_all()
        ResponseValidator(response).status(200)

        data = response.json()
        experience = data["experience"]

        assert len(experience) > 0, "Справочник опыта пуст"
        for item in experience:
            assert "id" in item, "Отсутствует поле 'id'"
            assert "name" in item, "Отсутствует поле 'name'"

    @pytest.mark.api
    @allure.title("Значения типа занятости содержат id и name")
    def test_employment_structure(
        self,
        dictionaries_api: DictionariesApi,
    ):
        response = dictionaries_api.get_all()
        ResponseValidator(response).status(200)

        data = response.json()
        employment = data["employment"]

        assert len(employment) > 0, "Справочник занятости пуст"
        for item in employment:
            assert "id" in item
            assert "name" in item

    @pytest.mark.api
    @allure.title("Известные ID опыта присутствуют")
    def test_known_experience_ids(
        self,
        dictionaries_api: DictionariesApi,
    ):
        response = dictionaries_api.get_all()
        ResponseValidator(response).status(200)

        data = response.json()
        ids = [item["id"] for item in data["experience"]]

        expected_ids = ["noExperience", "between1And3"]
        for expected_id in expected_ids:
            assert expected_id in ids, f"ID '{expected_id}' не найден"


@allure.feature("Dictionaries API")
@allure.story("Производительность")
class TestDictionariesPerformance:
    @pytest.mark.api
    @allure.title("Время ответа API справочников")
    def test_dictionaries_response_time(
        self,
        dictionaries_api: DictionariesApi,
        test_data: dict,
    ):
        response = dictionaries_api.get_all()

        ResponseValidator(response).status(200).response_time_under(
            test_data["expected_response_times"]["dictionaries"]
        ).raise_if_errors()
