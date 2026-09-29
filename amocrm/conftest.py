"""Global pytest configuration and fixtures."""

import logging
import sys

import pytest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get base URL for tests."""
    import os

    return os.getenv("APP_URL", "http://localhost:8080")
