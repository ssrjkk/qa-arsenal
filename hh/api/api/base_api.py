from typing import Any, Dict, Optional

import requests

from core.http_client import HTTPClient
from utils.logger import logger


class BaseApi:
    def __init__(self, client: HTTPClient) -> None:
        self.client = client
        logger.debug(f"{self.__class__.__name__} инициализирован")

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.client.get(path, params=params, headers=headers)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.client.post(path, json=json, headers=headers)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.client.put(path, json=json, headers=headers)

    def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self.client.delete(path, headers=headers)
