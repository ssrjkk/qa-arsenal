from typing import Any, Dict, List, Optional

from jsonschema import Draft7Validator, ValidationError

from utils.logger import logger


class SchemaValidator:
    def __init__(self, schema: Dict[str, Any]) -> None:
        self.schema = schema
        self.validator = Draft7Validator(schema)
        self.errors: List[str] = []

    def validate(self, instance: Any) -> "SchemaValidator":
        errors = list(self.validator.iter_errors(instance))
        if errors:
            for error in errors:
                error_msg = f"Schema validation error: {error.message} в пути {'.'.join(str(p) for p in error.path)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
        return self

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def raise_if_errors(self) -> None:
        if self.errors:
            raise ValidationError("\n".join(self.errors))


def validate_json_schema(instance: Any, schema: Dict[str, Any]) -> List[str]:
    validator = Draft7Validator(schema)
    errors = []

    for error in sorted(validator.iter_errors(instance), key=str):
        error_msg = f"Path: {' -> '.join(str(p) for p in error.path)}, Error: {error.message}"
        errors.append(error_msg)

    return errors


def validate_schema(instance: Any, schema: Dict[str, Any]) -> List[str]:
    """Alias for validate_json_schema for convenience"""
    return validate_json_schema(instance, schema)


def create_response_schema(
    required_fields: Optional[List[str]] = None,
    properties: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": properties or {},
    }

    if required_fields:
        schema["required"] = required_fields

    return schema
