import os
import threading
import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import get_config
from utils.logger import logger


class HTTPClient:
    """
    HTTP клиент с поддержкой:
    - автоматических retry на 5xx
    - троттлинга (отключается в CI)
    - логирования запросов/ответов
    - connection pooling
    """

    _lock = threading.Lock()
    _last_request_time: float = 0.0

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        skip_throttle: bool = False,
    ) -> None:
        config = get_config()

        self.base_url = base_url or config.base_url
        self.timeout = timeout or config.timeout
        self.max_retries = max_retries
        self.skip_throttle = skip_throttle or os.getenv("CI") == "true"

        self.session = requests.Session()
        self._setup_session()

        logger.info(
            f"HTTPClient initialized: base_url={self.base_url}, timeout={self.timeout}, skip_throttle={self.skip_throttle}"
        )

    def _setup_session(self) -> None:
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        retry_strategy = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _throttle(self) -> None:
        if self.skip_throttle:
            return

        with HTTPClient._lock:
            elapsed = time.monotonic() - HTTPClient._last_request_time
            min_interval = float(os.getenv("MIN_REQUEST_INTERVAL", "1.0"))
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            HTTPClient._last_request_time = time.monotonic()

    def _build_url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.base_url}{path}"

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        logger.debug(f"{method} {url} params={kwargs.get('params')} json={kwargs.get('json')}")

    def _log_response(
        self,
        method: str,
        url: str,
        response: requests.Response,
        start_time: float,
    ) -> None:
        elapsed_ms = (time.time() - start_time) * 1000

        if response.status_code >= 500:
            logger.warning(
                f"{method} {url} -> {response.status_code} ({elapsed_ms:.0f}ms) [SERVER ERROR]"
            )
        elif response.status_code >= 400:
            logger.warning(f"{method} {url} -> {response.status_code} ({elapsed_ms:.0f}ms)")
        else:
            logger.info(f"{method} {url} -> {response.status_code} ({elapsed_ms:.0f}ms)")

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Универсальный метод для HTTP запросов"""
        self._throttle()
        url = self._build_url(path)
        self._log_request(method, url, params=params, json=json)

        start_time = time.time()
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
            self._log_response(method, url, response, start_time)
            return response
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout on {method} {url}: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ConnectionError on {method} {url}: {e}")
            raise

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.request("POST", path, json=json, headers=headers)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.request("PUT", path, json=json, headers=headers)

    def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.request("DELETE", path, headers=headers)

    def close(self) -> None:
        self.session.close()
        logger.info("HTTPClient session closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
