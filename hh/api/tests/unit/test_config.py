"""Hermetic unit tests for configuration (no network)."""

import os

import pytest

from core.config import Config, get_config


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    for key in ["BASE_URL", "TIMEOUT", "MAX_RETRIES", "RETRY_DELAY", "LOG_LEVEL"]:
        monkeypatch.delenv(key, raising=False)


class TestGetConfig:
    def test_defaults(self):
        cfg = get_config()
        assert cfg.base_url == "https://api.hh.ru"
        assert cfg.timeout == 30
        assert cfg.max_retries == 5
        assert cfg.retry_delay == 2.0
        assert cfg.log_level == "INFO"

    def test_environment_overrides(self, monkeypatch):
        monkeypatch.setenv("BASE_URL", "https://stub.hh.ru")
        monkeypatch.setenv("TIMEOUT", "10")
        monkeypatch.setenv("MAX_RETRIES", "1")
        monkeypatch.setenv("RETRY_DELAY", "0.5")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        cfg = get_config()
        assert cfg.base_url == "https://stub.hh.ru"
        assert cfg.timeout == 10
        assert cfg.max_retries == 1
        assert cfg.retry_delay == 0.5
        assert cfg.log_level == "DEBUG"

    def test_config_is_dataclass(self):
        cfg = get_config()
        assert isinstance(cfg, Config)


class TestGetEnv:
    def test_with_default(self, monkeypatch):
        monkeypatch.delenv("SOME_VAR", raising=False)
        from core.config import get_env

        assert get_env("SOME_VAR", "fallback") == "fallback"

    def test_returns_set_value(self, monkeypatch):
        monkeypatch.setenv("SOME_VAR", "value")
        from core.config import get_env

        assert get_env("SOME_VAR", "fallback") == "value"