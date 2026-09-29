import requests

from api.base_api import BaseApi


class DictionariesApi(BaseApi):
    ENDPOINT = "/dictionaries"

    def get_all(self) -> requests.Response:
        return self.get(self.ENDPOINT)

    def get_by_name(self, dictionary_name: str) -> requests.Response:
        path = f"{self.ENDPOINT}/{dictionary_name}"
        return self.get(path)
