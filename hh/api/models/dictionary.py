from typing import List

from models.base_model import БазовыйМодель


class DictionaryItem(БазовыйМодель):
    id: str
    name: str


class DictionariesResponse(БазовыйМодель):
    vacancy_type: List[DictionaryItem] = []
    experience: List[DictionaryItem] = []
    employment: List[DictionaryItem] = []
    schedule: List[DictionaryItem] = []
    language: List[DictionaryItem] = []
    professional_role: List[DictionaryItem] = []
    employer_type: List[DictionaryItem] = []
    org_type: List[DictionaryItem] = []
    education_level: List[DictionaryItem] = []
