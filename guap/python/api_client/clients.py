from typing import List, Dict, Any
from .base import BaseApiClient


class GuapApiClient(BaseApiClient):
    """Client for GUAP API"""

    def get_students(self) -> List[Dict[str, Any]]:
        return self.get("/api/students").json()

    def get_student_by_id(self, student_id: int) -> Dict[str, Any]:
        return self.get(f"/api/students/{student_id}").json()

    def get_schedule(self, group: str = None) -> List[Dict[str, Any]]:
        params = {"group": group} if group else {}
        return self.get("/api/schedule", params=params).json()

    def get_subjects(self) -> List[Dict[str, Any]]:
        return self.get("/api/subjects").json()

    def get_grades(self, student_id: int = None) -> List[Dict[str, Any]]:
        params = {"student_id": student_id} if student_id else {}
        return self.get("/api/grades", params=params).json()

    def health_check(self) -> Dict[str, Any]:
        return self.get("/api/health").json()


class GenericApiClient(BaseApiClient):
    """Generic API client for any REST endpoint"""

    def get(self, endpoint: str, params: dict = None) -> Any:
        response = super().get(endpoint, params=params)
        return response.json() if response.text else None

    def post(self, endpoint: str, data: dict = None) -> Any:
        response = super().post(endpoint, json=data)
        return response.json() if response.text else None

    def put(self, endpoint: str, data: dict = None) -> Any:
        response = super().put(endpoint, json=data)
        return response.json() if response.text else None

    def patch(self, endpoint: str, data: dict = None) -> Any:
        response = super().patch(endpoint, json=data)
        return response.json() if response.text else None

    def delete(self, endpoint: str) -> Any:
        response = super().delete(endpoint)
        return response.json() if response.text else None
