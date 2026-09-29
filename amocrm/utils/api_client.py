"""HTTP Client utilities."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict

from core.config import get_app_url
from core.logger import get_logger

logger = get_logger("utils.http")


class HTTPClient:
    """Base HTTP client with retry and logging."""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or get_app_url()
        self.token = token
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Setup session with retry strategy."""
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self) -> Dict[str, str]:
        """Build request headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make HTTP request."""
        url = f"{self.base_url}{path}"
        logger.info(f"{method} {url}")

        response = self.session.request(method, url, headers=self._headers(), **kwargs)

        logger.info(f"Status: {response.status_code}")
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        """GET request."""
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        """POST request."""
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        """PUT request."""
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        """PATCH request."""
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        """DELETE request."""
        return self.request("DELETE", path, **kwargs)


class APIError(Exception):
    """API error exception."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code}: {message}")
