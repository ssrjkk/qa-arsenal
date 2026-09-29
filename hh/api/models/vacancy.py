from typing import Any, Dict, List, Optional

from models.base_model import БазовыйМодель


class Salary(БазовыйМодель):
    from_value: Optional[int] = None
    to_value: Optional[int] = None
    currency: Optional[str] = None
    gross: Optional[bool] = None


class Employer(БазовыйМодель):
    id: str
    name: str
    alternate_url: Optional[str] = None
    logo_urls: Optional[Dict[str, str]] = None
    trusted: Optional[bool] = None


class Area(БазовыйМодель):
    id: str
    name: str
    url: Optional[str] = None


class Vacancy(БазовыйМодель):
    id: str
    name: str
    employer: Optional[Dict[str, Any]] = None
    area: Optional[Dict[str, Any]] = None
    salary: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    experience: Optional[Dict[str, str]] = None
    employment: Optional[Dict[str, str]] = None
    schedule: Optional[Dict[str, str]] = None
    alternate_url: Optional[str] = None
    published_at: Optional[str] = None
    created_at: Optional[str] = None
    response_url: Optional[str] = None


class VacancySearchResponse(БазовыйМодель):
    items: List[Vacancy]
    found: int = 0
    pages: int = 1
    per_page: int = 10
    page: int = 0
    clusters: Optional[List[Any]] = None
    arguments: Optional[Dict[str, Any]] = None
    fixes: Optional[Dict[str, Any]] = None
