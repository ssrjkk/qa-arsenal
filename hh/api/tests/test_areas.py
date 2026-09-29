import allure
import pytest

from api.areas_api import AreasApi
from validators.response_validator import ResponseValidator


@allure.feature("Areas API")
@allure.story("Список регионов")
class TestAreas:
    @pytest.mark.api
    @pytest.mark.smoke
    @allure.title("Список регионов возвращает 200 и непустой")
    def test_areas_list(
        self,
        areas_api: AreasApi,
    ):
        response = areas_api.get_all()

        ResponseValidator(response).status(200).json_path(
            "$", lambda x: isinstance(x, list) and len(x) > 0
        ).raise_if_errors()

    @pytest.mark.api
    @allure.title("Элемент региона содержит обязательные поля")
    def test_area_item_structure(
        self,
        areas_api: AreasApi,
    ):
        response = areas_api.get_all()

        ResponseValidator(response).status(200)
        areas = response.json()

        assert isinstance(areas, list), "Ответ должен быть списком"
        assert len(areas) > 0, "Список регионов пуст"
        area = areas[0]

        for field in ["id", "name", "areas"]:
            assert field in area, f"Поле '{field}' отсутствует в регионе"


@allure.feature("Areas API")
@allure.story("Поиск регионов")
class TestAreaSearch:
    @pytest.mark.api
    @allure.title("Россия присутствует в списке регионов")
    def test_russia_in_areas(
        self,
        areas_api: AreasApi,
    ):
        response = areas_api.get_all()
        ResponseValidator(response).status(200)

        areas = response.json()
        names = [a["name"] for a in areas]

        assert any("Россия" in name for name in names), "Россия не найдена в регионах"

    @pytest.mark.api
    @allure.title("Санкт-Петербург присутствует в подрегионах России")
    def test_spb_in_russia(
        self,
        areas_api: AreasApi,
    ):
        response = areas_api.get_all()
        ResponseValidator(response).status(200)

        areas = response.json()
        russia = next((a for a in areas if "Россия" in a["name"]), None)
        assert russia is not None, "Россия не найдена"

        spb = next((a for a in russia["areas"] if a["id"] == "2"), None)
        assert spb is not None, "Санкт-Петербург (id=2) не найден"


@allure.feature("Areas API")
@allure.story("Получение региона по ID")
class TestAreaById:
    @pytest.mark.api
    @allure.title("Получение региона по ID")
    def test_get_area_by_id(
        self,
        areas_api: AreasApi,
    ):
        response = areas_api.get_by_id("1")

        ResponseValidator(response).status(200).has_keys(["id", "name"]).raise_if_errors()


@allure.feature("Areas API")
@allure.story("Производительность")
class TestAreasPerformance:
    @pytest.mark.api
    @allure.title("Время ответа API регионов")
    def test_areas_response_time(
        self,
        areas_api: AreasApi,
        test_data: dict,
    ):
        response = areas_api.get_all()

        ResponseValidator(response).status(200).response_time_under(
            test_data["expected_response_times"]["areas"]
        ).raise_if_errors()
