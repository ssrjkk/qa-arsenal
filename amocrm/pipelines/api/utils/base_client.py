"""Base API Client with retry logic and error handling."""

import requests
from typing import Optional, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for API clients with common functionality."""

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        self._setup_session(max_retries)
        self._headers = self._build_headers()

    def _setup_session(self, max_retries: int):
        """Configure session with retry strategy."""
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make HTTP request with logging."""
        url = f"{self.base_url}{path}"
        logger.info(f"[{method}] {url}")

        try:
            response = self.session.request(
                method=method, url=url, headers=self._headers, timeout=self.timeout, **kwargs
            )
            logger.info(f"Status: {response.status_code}")
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Timeout: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise

    def get(self, path: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)

    def set_token(self, token: str):
        """Update authentication token."""
        self.token = token
        self._headers = self._build_headers()

    def close(self):
        """Close session."""
        self.session.close()
