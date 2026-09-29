import logging
import time
from typing import Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import config

logger = logging.getLogger(__name__)


class BaseApiClient:
    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None):
        self.base_url = base_url or config.BASE_URL
        self._session = session or self._create_session()
        self._last_request_time = 0
        self._min_request_interval = 0.1

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _log_request(self, method: str, url: str, **kwargs):
        logger.info(f"REQUEST: {method} {url}")
        if "params" in kwargs:
            logger.debug(f"PARAMS: {kwargs['params']}")
        if "json" in kwargs:
            logger.debug(f"BODY: {kwargs['json']}")

    def _log_response(self, response: requests.Response):
        logger.info(f"RESPONSE: {response.status_code} {response.url}")
        logger.debug(f"BODY: {response.text[:500]}")

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        expected_status: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        self._rate_limit()

        url = urljoin(self.base_url, endpoint)
        self._log_request(method, url, params=params, json=json)

        response = self._session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            timeout=timeout or config.TIMEOUT_PAGE_LOAD
        )

        self._log_response(response)

        if expected_status and response.status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {response.status_code}. "
                f"Response: {response.text[:500]}"
            )

        return response

    def get(self, endpoint: str, params: Optional[dict] = None, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, json=json, **kwargs)

    def put(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, json=json, **kwargs)

    def patch(self, endpoint: str, json: Optional[dict] = None, **kwargs) -> requests.Response:
        return self.request("PATCH", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()