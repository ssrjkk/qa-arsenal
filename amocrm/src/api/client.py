"""AmoCRM API v4 Client."""

import requests
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import get_amocrm_api_url, get_amocrm_token
from core.logger import get_logger

logger = get_logger("api.client")


class AmoCRMClient:
    """Client для amoCRM API v4."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.base_url = base_url or get_amocrm_api_url()
        self.token = token or get_amocrm_token()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        logger.info(f"{method} {url}")
        response = self.session.request(method, url, headers=self._headers(), **kwargs)
        logger.info(f"Status: {response.status_code}")
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    # === Entities ===
    def get_account(self) -> requests.Response:
        return self.get("/account")

    def list_contacts(self, **params) -> requests.Response:
        return self.get("/contacts", params=params)

    def get_contact(self, contact_id: int) -> requests.Response:
        return self.get(f"/contacts/{contact_id}")

    def create_contact(self, data: dict) -> requests.Response:
        return self.post("/contacts", json=[data])

    def update_contact(self, contact_id: int, data: dict) -> requests.Response:
        return self.patch(f"/contacts/{contact_id}", json=[data])

    def delete_contact(self, contact_id: int) -> requests.Response:
        return self.delete(f"/contacts/{contact_id}")

    def list_leads(self, **params) -> requests.Response:
        return self.get("/leads", params=params)

    def create_lead(self, data: dict) -> requests.Response:
        return self.post("/leads", json=[data])

    def list_companies(self, **params) -> requests.Response:
        return self.get("/companies", params=params)

    def list_pipelines(self) -> requests.Response:
        return self.get("/leads/pipelines")

    def list_users(self) -> requests.Response:
        return self.get("/users")

    def list_tasks(self, **params) -> requests.Response:
        return self.get("/tasks", params=params)

    def list_tags(self) -> requests.Response:
        return self.get("/tags")
