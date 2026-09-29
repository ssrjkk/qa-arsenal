import pytest

from api.areas_api import AreasApi
from api.dictionaries_api import DictionariesApi
from api.vacancies_api import VacanciesApi


@pytest.mark.ci
class TestCISmoke:
    def test_vacancies_api_responds(self, vacancies_api: VacanciesApi) -> None:
        response = vacancies_api.search(text="python", per_page=1)
        assert response.status_code in [200, 429, 403]

    def test_areas_api_responds(self, areas_api: AreasApi) -> None:
        response = areas_api.get_all()
        assert response.status_code in [200, 429, 403]

    def test_dictionaries_api_responds(self, dictionaries_api: DictionariesApi) -> None:
        response = dictionaries_api.get_all()
        assert response.status_code in [200, 429, 403]
