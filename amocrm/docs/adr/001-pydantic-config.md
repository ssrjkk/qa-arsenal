# ADR-001: Use Pydantic v2 for Configuration Management

## Status
Accepted

## Context
We need a type-safe, validated configuration system that:
- Supports multiple environments (dev, stage, prod)
- Validates configuration at startup
- Provides clear error messages for misconfiguration
- Works with 12-factor app principles

## Decision
We will use **Pydantic v2** with `pydantic-settings` for all configuration management.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Pydantic v2** | Type safety, validation, env override | Learning curve |
| | Fast, well-documented | |
| ConfigParser | Simple | No validation, no typing |
| dataclasses | Built-in | Manual validation needed |
| Hydra | Flexible | Overkill for our needs |
| | | Complex |

## Implementation

```python
# core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    
    @property
    def db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
```

## Consequences

### Positive
- ✅ Type safety at runtime
- ✅ Validation at startup (fail fast)
- ✅ Environment variable override
- ✅ Easy to test with fixtures

### Negative
- ❌ Additional dependency
- ❌ Learning curve for team

## References
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)
- [12-factor App Config](https://12factor.net/config)