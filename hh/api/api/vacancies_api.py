from typing import Any, Dict, List, Optional

import requests

from api.base_api import BaseApi


class VacanciesApi(BaseApi):
    ENDPOINT = "/vacancies"

    def search(
        self,
        text: Optional[str] = None,
        area: Optional[str] = None,
        per_page: int = 10,
        page: int = 0,
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        salary: Optional[int] = None,
        currency: Optional[str] = None,
    ) -> requests.Response:
        params: Dict[str, Any] = {
            "per_page": per_page,
            "page": page,
        }

        if text:
            params["text"] = text
        if area:
            params["area"] = area
        if experience:
            params["experience"] = experience
        if employment:
            params["employment"] = employment
        if schedule:
            params["schedule"] = schedule
        if salary is not None:
            params["salary"] = salary
        if currency:
            params["currency"] = currency

        return self.get(self.ENDPOINT, params=params)

    def get_by_id(self, vacancy_id: str) -> requests.Response:
        path = f"{self.ENDPOINT}/{vacancy_id}"
        return self.get(path)

    def get_by_ids(self, vacancy_ids: List[str]) -> List[requests.Response]:
        return [self.get_by_id(vacancy_id) for vacancy_id in vacancy_ids]

    def similar_vacancies(self, vacancy_id: str) -> requests.Response:
        path = f"{self.ENDPOINT}/{vacancy_id}/similar_vacancies"
        return self.get(path)
