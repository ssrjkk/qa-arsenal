"""Hermetic unit tests for HTTPClient (mocked transport, no real network)."""

from types import SimpleNamespace

import pytest

from core.http_client import HTTPClient


@pytest.fixture
def client():
    c = HTTPClient(base_url="https://stub.hh.ru", timeout=5, max_retries=1, skip_throttle=True)
    yield c
    c.close()


class TestBuildUrl:
    def test_relative_path(self, client):
        assert client._build_url("/vacancies") == "https://stub.hh.ru/vacancies"

    def test_absolute_url_kept(self, client):
        assert client._build_url("https://other.example/x") == "https://other.example/x"


class TestRequest:
    def test_get_success(self, client, monkeypatch):
        response = SimpleNamespace(status_code=200, text="{}", url="u")

        def fake_request(method, url, params=None, json=None, headers=None, timeout=None):
            return response

        monkeypatch.setattr(client.session, "request", fake_request)
        r = client.get("/vacancies", params={"text": "qa"})
        assert r.status_code == 200

    def test_timeout_raises(self, client, monkeypatch):
        import requests

        def fake_request(method, url, params=None, json=None, headers=None, timeout=None):
            raise requests.exceptions.Timeout()

        monkeypatch.setattr(client.session, "request", fake_request)
        with pytest.raises(requests.exceptions.Timeout):
            client.get("/vacancies")

    def test_post_passes_json(self, client, monkeypatch):
        captured = {}

        def fake_request(method, url, params=None, json=None, headers=None, timeout=None):
            captured.update(method=method, url=url, json=json)
            return SimpleNamespace(status_code=200, text="{}", url="u")

        monkeypatch.setattr(client.session, "request", fake_request)
        client.post("/resumes", json={"title": "t"})
        assert captured["method"] == "POST"
        assert captured["url"] == "https://stub.hh.ru/resumes"
        assert captured["json"] == {"title": "t"}

    def test_headers_forwarded(self, client, monkeypatch):
        captured = {}

        def fake_request(method, url, params=None, json=None, headers=None, timeout=None):
            captured["headers"] = headers
            return SimpleNamespace(status_code=200, text="{}", url="u")

        monkeypatch.setattr(client.session, "request", fake_request)
        client.get("/x", headers={"X-Test": "1"})
        assert captured["headers"] == {"X-Test": "1"}