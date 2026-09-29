"""Hermetic unit tests for the API base client (fake session, no network)."""

import pytest

from api_client.base import BaseApiClient


class FakeResponse:
    def __init__(self, status_code=200, url="u", text="{}"):
        self.status_code = status_code
        self.url = url
        self.text = text

    def json(self):
        return {}


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, params=None, json=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params, "json": json, "timeout": timeout})
        return FakeResponse(200, url)


@pytest.fixture
def session():
    return FakeSession()


@pytest.fixture
def client(session):
    c = BaseApiClient(base_url="https://stub.example", session=session)
    # No throttling sleeps in tests.
    c._min_request_interval = 0
    return c


class TestRequest:
    def test_get_passes_url_and_params(self, client, session):
        client.get("/api/students", params={"group": "A"})
        call = session.calls[0]
        assert call["method"] == "GET"
        assert call["url"] == "https://stub.example/api/students"
        assert call["params"] == {"group": "A"}

    def test_post_passes_json(self, client, session):
        client.post("/api/students", json={"name": "alice"})
        call = session.calls[0]
        assert call["method"] == "POST"
        assert call["json"] == {"name": "alice"}

    def test_delete_maps_method(self, client, session):
        client.delete("/api/students/1")
        assert session.calls[0]["method"] == "DELETE"

    def test_patch_maps_method(self, client, session):
        client.patch("/api/students/1", json={"name": "bob"})
        assert session.calls[0]["method"] == "PATCH"

    def test_expected_status_match(self, client, session):
        client.get("/api/health", expected_status=200)

    def test_expected_status_mismatch_raises(self, client, session):
        with pytest.raises(AssertionError):
            client.get("/api/health", expected_status=404)


class TestRateLimit:
    def test_does_not_sleep_when_interval_zero(self, client, monkeypatch):
        slept = []

        def fake_sleep(seconds):
            slept.append(seconds)

        monkeypatch.setattr("api_client.base.time.sleep", fake_sleep)
        client._rate_limit()
        assert slept == []

    def test_sleeps_when_just_requested(self, client, monkeypatch):
        import api_client.base as base

        slept = []
        monkeypatch.setattr(base.time, "time", lambda: 100.0)
        monkeypatch.setattr(base.time, "sleep", lambda s: slept.append(s))

        client._last_request_time = 100.0
        client._min_request_interval = 0.5
        client._rate_limit()
        assert slept and slept[0] > 0


class TestUrlJoin:
    def test_relative_endpoint(self, client):
        assert client._session is not None
        from urllib.parse import urljoin

        assert urljoin("https://stub.example", "api/x") == "https://stub.example/api/x"