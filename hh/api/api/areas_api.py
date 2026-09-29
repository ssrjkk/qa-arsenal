import requests

from api.base_api import BaseApi


class AreasApi(BaseApi):
    ENDPOINT = "/areas"

    def get_all(self) -> requests.Response:
        return self.get(self.ENDPOINT)

    def get_by_id(self, area_id: str | int) -> requests.Response:
        path = f"{self.ENDPOINT}/{area_id}"
        return self.get(path)

    def get_metro_areas(self, area_id: str | int) -> requests.Response:
        path = f"/metro_areas/{area_id}"
        return self.get(path)

    def get_regions(self) -> requests.Response:
        params = {"type": "region"}
        return self.get(self.ENDPOINT, params=params)
