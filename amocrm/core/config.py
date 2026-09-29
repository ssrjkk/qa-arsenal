"""Core config for demo application."""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Demo App
    app_host: str = Field(default="localhost", alias="APP_HOST")
    app_port: int = Field(default=8080, alias="APP_PORT")
    app_url: str = Field(default="http://localhost:8080", alias="APP_URL")

    # Database
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="amocrm", alias="DB_NAME")
    db_user: str = Field(default="user", alias="DB_USER")
    db_password: str = Field(default="pass", alias="DB_PASSWORD")

    # AmoCRM
    amocrm_subdomain: str = Field(default="localhost", alias="AMOCRM_SUBDOMAIN")
    amocrm_token: str = Field(default="", alias="AMOCRM_LONG_TOKEN")
    amocrm_long_token: str = Field(default="", alias="AMOCRM_LONG_TOKEN")

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def amocrm_api_url(self) -> str:
        return f"https://{self.amocrm_subdomain}.amocrm.ru/api/v4"

    # Kafka
    kafka_bootstrap_servers: List[str] = Field(default=["localhost:9092"], alias="KAFKA_BROKERS")

    # Selenium
    selenium_grid_url: str = Field(default="http://localhost:4444/wd/hub", alias="SELENIUM_GRID")

    # Test config
    parallel_workers: str = Field(default="auto", alias="PARALLEL_WORKERS")
    allure_dir: str = Field(default="reports/allure-results", alias="ALLURE_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_app_url() -> str:
    """Get application URL."""
    return get_settings().app_url


def get_db_url() -> str:
    """Get database URL."""
    return get_settings().db_url


def get_amocrm_api_url() -> str:
    """Get AmoCRM API URL."""
    return get_settings().amocrm_api_url


def get_amocrm_token() -> str:
    """Get AmoCRM token."""
    return get_settings().amocrm_token
