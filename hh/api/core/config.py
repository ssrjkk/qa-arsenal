import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    base_url: str
    timeout: int
    max_retries: int
    retry_delay: float
    log_level: str


def get_config() -> Config:
    base_url = os.getenv("BASE_URL", "https://api.hh.ru")
    timeout = int(os.getenv("TIMEOUT", "30"))
    max_retries = int(os.getenv("MAX_RETRIES", "5"))
    retry_delay = float(os.getenv("RETRY_DELAY", "2.0"))
    log_level = os.getenv("LOG_LEVEL", "INFO")

    return Config(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        log_level=log_level,
    )


def get_env(name: str, default: Optional[str] = None) -> str:
    return os.getenv(name, default) if default else os.getenv(name, "")
