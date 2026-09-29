"""Hermetic unit tests for API clients (fake session, no network)."""

import pytest

from api_client.clients import GenericApiClient, GuapApiClient


class FakeResponse:
    def __init__(self, status_code=200, text="{}", url="https://stub"):
        self.status_code = status_code
        self.text = text
        self.url = url

    def json(self):
        import json

        return json.loads(self.text)


class FakeSession:
    def __init__(self, text="{}"):
        self.calls = []
        self.text = text

    def request(self, method, url, params=None, json=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params, "json": json})
        return FakeResponse(200, self.text, url)


@pytest.fixture
def session():
    return FakeSession('[{"id": 1}]')


@pytest.fixture
def client(session):
    c = GuapApiClient(base_url="https://stub.example", session=session)
    c._min_request_interval = 0
    return c


class TestGuapApiClientRoutes:
    def test_get_students(self, client, session):
        assert client.get_students() == [{"id": 1}]
        assert session.calls[0]["url"] == "https://stub.example/api/students"

    def test_get_student_by_id(self, client, session):
        client.get_student_by_id(42)
        assert session.calls[0]["url"] == "https://stub.example/api/students/42"

    def test_get_schedule_with_group(self, client, session):
        client.get_schedule(group="A")
        assert session.calls[0]["params"] == {"group": "A"}

    def test_get_schedule_without_group(self, client, session):
        client.get_schedule()
        assert session.calls[0]["params"] == {}

    def test_get_subjects(self, client, session):
        client.get_subjects()
        assert session.calls[0]["url"] == "https://stub.example/api/subjects"

    def test_get_grades_with_student(self, client, session):
        client.get_grades(student_id=7)
        assert session.calls[0]["params"] == {"student_id": 7}

    def test_health_check(self, client, session):
        client.health_check()
        assert session.calls[0]["url"] == "https://stub.example/api/health"


class TestGenericApiClient:
    @pytest.fixture
    def generic(self, session):
        c = GenericApiClient(base_url="https://stub.example", session=session)
        c._min_request_interval = 0
        return c

    def test_get_returns_parsed_json(self, generic):
        result = generic.get("/resource")
        assert result == [{"id": 1}]

    def test_get_returns_none_on_empty(self, generic, session):
        session.text = ""
        assert generic.get("/empty") is None

    def test_post_sends_json(self, generic, session):
        generic.post("/resource", data={"name": "x"})
        assert session.calls[0]["method"] == "POST"
        assert session.calls[0]["json"] == {"name": "x"}

    def test_put_and_patch_and_delete(self, generic, session):
        generic.put("/resource/1", data={"a": 1})
        generic.patch("/resource/1", data={"b": 2})
        generic.delete("/resource/1")
        assert [c["method"] for c in session.calls] == ["PUT", "PATCH", "DELETE"]