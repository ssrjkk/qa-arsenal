"""HTTP Client with connection pooling, retry logic, and logging."""

import logging
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import get_settings

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with session pooling and automatic retry on 5xx errors."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        settings = get_settings()
        self.base_url = base_url or settings.app_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        """Log outgoing request."""
        logger.debug(f"--> {method} {url}")
        if "params" in kwargs:
            logger.debug(f"    params: {kwargs['params']}")
        if "json" in kwargs:
            logger.debug(f"    json: {kwargs['json']}")

    def _log_response(self, response: requests.Response, elapsed: float) -> None:
        """Log incoming response."""
        logger.debug(f"<-- {response.status_code} {elapsed:.3f}s")

    def request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make HTTP request with retry."""
        url = self._build_url(endpoint)
        self._log_request(method, url, **kwargs)

        start = time.time()
        try:
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)
            elapsed = time.time() - start
            self._log_response(response, elapsed)
            return response
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start
            logger.error(f"<-- ERROR {elapsed:.3f}s: {e}")
            raise

    def get(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close session."""
        self.session.close()
