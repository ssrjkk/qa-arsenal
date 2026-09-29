"""Hermetic unit tests for the vacancies API layer (fake session, no network)."""

from types import SimpleNamespace

import pytest

from api.vacancies_api import VacanciesApi
from core.http_client import HTTPClient


class FakeResponse:
    def __init__(self, status_code=200, text="{}", url="u"):
        self.status_code = status_code
        self.text = text
        self.url = url

    def json(self):
        import json

        return json.loads(self.text)


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, params=None, json=None, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params})
        return FakeResponse(200, '{"items": []}', url)


@pytest.fixture
def api():
    client = HTTPClient(base_url="https://api.hh.ru", timeout=5, max_retries=1, skip_throttle=True)
    client.session = FakeSession()  # type: ignore[assignment]
    return VacanciesApi(client)


class TestSearch:
    def test_default_params(self, api):
        api.search()
        params = api.client.session.calls[0]["params"]
        assert params["per_page"] == 10
        assert params["page"] == 0

    def test_all_filters_included(self, api):
        api.search(text="qa", area="1", per_page=5, page=2, experience="between1And3", employment="full", schedule="fullDay", salary=100, currency="RUR")
        params = api.client.session.calls[0]["params"]
        assert params["text"] == "qa"
        assert params["area"] == "1"
        assert params["per_page"] == 5
        assert params["page"] == 2
        assert params["experience"] == "between1And3"
        assert params["salary"] == 100
        assert params["currency"] == "RUR"

    def test_optional_filters_omitted(self, api):
        api.search()
        params = api.client.session.calls[0]["params"]
        assert "text" not in params
        assert "salary" not in params
        assert "experience" not in params


class TestByPath:
    def test_get_by_id_path(self, api):
        api.get_by_id("123")
        assert api.client.session.calls[0]["url"] == "https://api.hh.ru/vacancies/123"

    def test_similar_vacancies_path(self, api):
        api.similar_vacancies("123")
        assert api.client.session.calls[0]["url"] == "https://api.hh.ru/vacancies/123/similar_vacancies"

    def test_get_by_ids_issues_one_request_each(self, api):
        api.get_by_ids(["1", "2", "3"])
        assert len(api.client.session.calls) == 3
        urls = [c["url"] for c in api.client.session.calls]
        assert urls == ["https://api.hh.ru/vacancies/1", "https://api.hh.ru/vacancies/2", "https://api.hh.ru/vacancies/3"]