"""Response validator with Fluent DSL."""

import logging
from typing import Any, Callable

import requests

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Fluent DSL for response validation."""

    def __init__(self, response: requests.Response):
        self._response = response
        self._errors: list[str] = []

    @property
    def response(self) -> requests.Response:
        """Get response object."""
        return self._response

    @property
    def json(self) -> dict:
        """Get JSON response."""
        try:
            return self._response.json()
        except Exception:
            return {}

    def status(self, expected: int) -> "ResponseValidator":
        """Assert status code."""
        if self._response.status_code != expected:
            self._errors.append(f"Expected status {expected}, got {self._response.status_code}")
        return self

    def status_2xx(self) -> "ResponseValidator":
        """Assert 2xx status code."""
        if not 200 <= self._response.status_code < 300:
            self._errors.append(f"Expected 2xx, got {self._response.status_code}")
        return self

    def has_key(self, key: str) -> "ResponseValidator":
        """Assert JSON has key."""
        if key not in self.json:
            self._errors.append(f"Missing key: {key}")
        return self

    def has_keys(self, keys: list[str]) -> "ResponseValidator":
        """Assert JSON has keys."""
        for key in keys:
            self.has_key(key)
        return self

    def json_path(self, path: str, check: Callable[[Any], bool]) -> "ResponseValidator":
        """Check value at JSON path."""
        try:
            value = self.json.get(path)
            if not check(value):
                self._errors.append(f"Path '{path}' failed check: {value}")
        except Exception as e:
            self._errors.append(f"Path '{path}' error: {e}")
        return self

    def response_time_under(self, ms: int) -> "ResponseValidator":
        """Assert response time under limit."""
        elapsed = self._response.elapsed.total_seconds() * 1000
        if elapsed > ms:
            self._errors.append(f"Response time {elapsed:.0f}ms exceeds {ms}ms")
        return self

    def data_count(self, min_count: int = 0) -> "ResponseValidator":
        """Assert data array has minimum count."""
        data = (
            self.json.get("data")
            or self.json.get("users")
            or self.json.get("contacts")
            or self.json.get("companies")
            or self.json.get("deals")
            or []
        )
        if len(data) < min_count:
            self._errors.append(f"Data count {len(data)} < {min_count}")
        return self

    def raise_if_errors(self) -> None:
        """Raise exception if validation errors found."""
        if self._errors:
            error_msg = "; ".join(self._errors)
            logger.error(f"Validation failed: {error_msg}")
            raise AssertionError(error_msg)

    def model(self, model_cls: type[Any]) -> Any:
        """Parse response into Pydantic model."""
        return model_cls.model_validate(self.json)
