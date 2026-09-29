"""Base API class with common HTTP methods."""

import logging
from typing import Any, Dict, Optional

import requests

from core.http_client import HTTPClient

logger = logging.getLogger(__name__)


class BaseApi:
    """Base API class with common operations."""

    ENDPOINT: str = ""

    def __init__(self, http_client: Optional[HTTPClient] = None):
        self._http = http_client or HTTPClient()

    @property
    def client(self) -> HTTPClient:
        """Get HTTP client."""
        return self._http

    def _build_params(self, **kwargs: Any) -> Dict[str, Any]:
        """Filter None values from params."""
        return {k: v for k, v in kwargs.items() if v is not None}

    def get(self, path: str = "", **params: Any) -> requests.Response:
        """GET request."""
        endpoint = f"{self.ENDPOINT}/{path}".strip("/")
        return self._http.get(endpoint, params=self._build_params(**params))

    def post(self, path: str = "", **data: Any) -> requests.Response:
        """POST request."""
        endpoint = f"{self.ENDPOINT}/{path}".strip("/")
        return self._http.post(endpoint, json=self._build_params(**data))

    def put(self, path: str = "", **data: Any) -> requests.Response:
        """PUT request."""
        endpoint = f"{self.ENDPOINT}/{path}".strip("/")
        return self._http.put(endpoint, json=self._build_params(**data))

    def delete(self, path: str = "", **params: Any) -> requests.Response:
        """DELETE request."""
        endpoint = f"{self.ENDPOINT}/{path}".strip("/")
        return self._http.delete(endpoint, params=self._build_params(**params))

    def get_list(self, path: str = "", page: int = 1, per_page: int = 20, **params: Any) -> requests.Response:
        """GET with pagination."""
        return self.get(path, page=page, per_page=per_page, **params)
