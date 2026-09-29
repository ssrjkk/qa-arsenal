from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class FieldSchema:
    name: str
    required: bool = True
    type: Optional[type] = None
    nullable: bool = False
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    items_schema: Optional["FieldSchema"] = None


@dataclass
class Schema:
    fields: List[FieldSchema]
    allow_extra_fields: bool = True


class ValidationError(Exception):
    pass


def validate_type(value: Any, expected_type: type, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Field '{field_name}': expected {expected_type.__name__}, got {type(value).__name__}"
        )


def validate_pattern(value: str, pattern: str, field_name: str) -> None:
    if value and not re.match(pattern, str(value)):
        raise ValidationError(
            f"Field '{field_name}': value '{value}' does not match pattern '{pattern}'"
        )


def validate_length(value: Any, min_len: Optional[int], max_len: Optional[int], field_name: str) -> None:
    if min_len is not None and len(value) < min_len:
        raise ValidationError(
            f"Field '{field_name}': length {len(value)} is less than minimum {min_len}"
        )
    if max_len is not None and len(value) > max_len:
        raise ValidationError(
            f"Field '{field_name}': length {len(value)} exceeds maximum {max_len}"
        )


def validate_field(value: Any, schema: FieldSchema, path: str) -> None:
    if value is None:
        if schema.required:
            raise ValidationError(f"Required field '{path}' is missing")
        if not schema.nullable:
            return

    if schema.type is not None:
        validate_type(value, schema.type, path)

    if schema.pattern is not None:
        validate_pattern(value, schema.pattern, path)

    if schema.min_length is not None or schema.max_length is not None:
        validate_length(value, schema.min_length, schema.max_length, path)

    if isinstance(value, list) and schema.items_schema is not None:
        for i, item in enumerate(value):
            validate_field(item, schema.items_schema, f"{path}[{i}]")


def validate_object(data: Any, schema: Schema, path: str = "") -> List[str]:
    errors = []

    if not isinstance(data, dict):
        return [f"Expected object, got {type(data).__name__}"]

    for field_schema in schema.fields:
        field_path = f"{path}.{field_schema.name}" if path else field_schema.name
        value = data.get(field_schema.name)

        try:
            validate_field(value, field_schema, field_path)
        except ValidationError as e:
            errors.append(str(e))

    return errors


class ResponseValidator:
    @staticmethod
    def validate_user(data: Dict[str, Any]) -> List[str]:
        return validate_object(data, Schema([
            FieldSchema("id", type=int),
            FieldSchema("name", type=str, min_length=1),
            FieldSchema("username", type=str, min_length=1),
            FieldSchema("email", type=str, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"),
            FieldSchema("phone", type=str),
            FieldSchema("website", type=str),
        ]))

    @staticmethod
    def validate_post(data: Dict[str, Any]) -> List[str]:
        return validate_object(data, Schema([
            FieldSchema("id", type=int),
            FieldSchema("userId", type=int),
            FieldSchema("title", type=str, min_length=1),
            FieldSchema("body", type=str, min_length=1),
        ]))

    @staticmethod
    def validate_todo(data: Dict[str, Any]) -> List[str]:
        return validate_object(data, Schema([
            FieldSchema("id", type=int),
            FieldSchema("userId", type=int),
            FieldSchema("title", type=str, min_length=1),
            FieldSchema("completed", type=bool),
        ]))

    @staticmethod
    def validate_comment(data: Dict[str, Any]) -> List[str]:
        return validate_object(data, Schema([
            FieldSchema("id", type=int),
            FieldSchema("postId", type=int),
            FieldSchema("name", type=str, min_length=1),
            FieldSchema("email", type=str, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"),
            FieldSchema("body", type=str, min_length=1),
        ]))

    @staticmethod
    def validate_user_list(data: List[Dict[str, Any]]) -> List[str]:
        errors = []
        for i, user in enumerate(data):
            errors.extend(ResponseValidator.validate_user(user))
        return errors

    @staticmethod
    def validate_post_list(data: List[Dict[str, Any]]) -> List[str]:
        errors = []
        for i, post in enumerate(data):
            errors.extend(ResponseValidator.validate_post(post))
        return errors

    @staticmethod
    def validate_todo_list(data: List[Dict[str, Any]]) -> List[str]:
        errors = []
        for i, todo in enumerate(data):
            errors.extend(ResponseValidator.validate_todo(todo))
        return errors