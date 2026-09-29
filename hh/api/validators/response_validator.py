import json
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

import requests
from pydantic import BaseModel, ValidationError

from utils.logger import logger

T = TypeVar("T", bound=BaseModel)


class ResponseValidator:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self._data: Optional[Dict[str, Any]] = None
        self._errors: List[str] = []

    @property
    def data(self) -> Dict[str, Any]:
        if self._data is None:
            try:
                self._data = self.response.json()
            except json.JSONDecodeError:
                self._data = {}
                self._errors.append(f"Не удалось распарсить JSON: {self.response.text[:200]}")
        return self._data

    def status(self, expected: int) -> "ResponseValidator":
        if self.response.status_code != expected:
            error_msg = (
                f"Ожидался статус {expected}, получен {self.response.status_code}. "
                f"Тело: {self.response.text[:500]}"
            )
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def status_in(self, expected: List[int]) -> "ResponseValidator":
        if self.response.status_code not in expected:
            error_msg = (
                f"Ожидался статус из {expected}, получен {self.response.status_code}. "
                f"Тело: {self.response.text[:500]}"
            )
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def json_path(
        self, path: str, validator: Optional[Callable[[Any], bool]] = None
    ) -> "ResponseValidator":
        if path == "$":
            return self._validate_root(validator)

        keys = path.split(".")
        current = self.data

        for key in keys:
            if isinstance(current, dict):
                if key not in current:
                    error_msg = f"Путь '{path}' не найден. Доступные ключи: {list(current.keys())}"
                    self._errors.append(error_msg)
                    logger.error(error_msg)
                    return self
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key)
                    current = current[index]
                except (ValueError, IndexError):
                    error_msg = f"Не удалось получить индекс {key} из списка"
                    self._errors.append(error_msg)
                    return self
            else:
                error_msg = f"Невозможно пройти по пути '{path}'"
                self._errors.append(error_msg)
                return self

        if validator is not None:
            try:
                if not validator(current):
                    error_msg = f"Валидация пути '{path}' не прошла. Значение: {current}"
                    self._errors.append(error_msg)
                    logger.error(error_msg)
            except Exception as e:
                error_msg = f"Ошибка валидации пути '{path}': {e}"
                self._errors.append(error_msg)
                logger.error(error_msg)

        return self

    def _validate_root(
        self, validator: Optional[Callable[[Any], bool]] = None
    ) -> "ResponseValidator":
        current = self.data
        if validator is not None:
            try:
                if not validator(current):
                    error_msg = f"Валидация корня не прошла. Значение: {current}"
                    self._errors.append(error_msg)
                    logger.error(error_msg)
            except Exception as e:
                error_msg = f"Ошибка валидации корня: {e}"
                self._errors.append(error_msg)
                logger.error(error_msg)
        return self

    def has_key(self, key: str) -> "ResponseValidator":
        if key not in self.data:
            error_msg = f"Ключ '{key}' не найден. Доступные ключи: {list(self.data.keys())}"
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def has_keys(self, keys: List[str]) -> "ResponseValidator":
        for key in keys:
            self.has_key(key)
        return self

    def key_equals(self, key: str, expected: Any) -> "ResponseValidator":
        actual = self.data.get(key)
        if actual != expected:
            error_msg = f"Ключ '{key}': ожидалось '{expected}', получено '{actual}'"
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def key_type(self, key: str, expected_type: Type) -> "ResponseValidator":
        actual = self.data.get(key)
        if actual is None:
            error_msg = f"Ключ '{key}' отсутствует"
            self._errors.append(error_msg)
            logger.error(error_msg)
        elif not isinstance(actual, expected_type):
            error_msg = (
                f"Ключ '{key}': ожидался тип {expected_type.__name__}, "
                f"получен {type(actual).__name__}"
            )
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def list_not_empty(self, key: str) -> "ResponseValidator":
        value = self.data.get(key)
        if not isinstance(value, list):
            error_msg = f"Ключ '{key}' не является списком"
            self._errors.append(error_msg)
            logger.error(error_msg)
        elif len(value) == 0:
            error_msg = f"Список '{key}' пуст"
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def list_length(self, key: str, expected_length: int) -> "ResponseValidator":
        value = self.data.get(key)
        if isinstance(value, list) and len(value) != expected_length:
            error_msg = f"Длина списка '{key}': ожидалась {expected_length}, получена {len(value)}"
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def list_max_length(self, key: str, max_length: int) -> "ResponseValidator":
        value = self.data.get(key)
        if isinstance(value, list) and len(value) > max_length:
            error_msg = (
                f"Длина списка '{key}': превышает максимум {max_length}, получена {len(value)}"
            )
            self._errors.append(error_msg)
            logger.error(error_msg)
        return self

    def response_time_under(self, ms: int) -> "ResponseValidator":
        elapsed = self.response.elapsed.total_seconds() * 1000
        if elapsed >= ms:
            error_msg = f"Время ответа {elapsed:.0f}мс превышает лимит {ms}мс"
            self._errors.append(error_msg)
            logger.warning(error_msg)
        return self

    def model(self, model_class: Type[T]) -> T:
        try:
            return model_class.model_validate(self.data)  # type: ignore[no-any-return]
        except ValidationError as e:
            error_msg = f"Ошибка валидации модели {model_class.__name__}: {e}"
            self._errors.append(error_msg)
            logger.error(error_msg)
            raise

    def raise_if_errors(self) -> None:
        if self._errors:
            error_text = "\n".join(self._errors)
            raise AssertionError(f"Валидация не прошла:\n{error_text}")
