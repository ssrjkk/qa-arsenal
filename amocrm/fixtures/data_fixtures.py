"""Pytest fixtures for test data."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def test_data() -> dict:
    """Load test data from JSON."""
    data_file = Path(__file__).parent.parent / "data" / "test_data.json"
    with open(data_file) as f:
        return json.load(f)


@pytest.fixture
def sample_contact():
    return {"name": "Test User", "email": "test@example.com", "phone": "+1234567890"}


@pytest.fixture
def sample_company():
    return {"name": "Test Company", "website": "https://test.com", "phone": "+1234567890"}


@pytest.fixture
def sample_deal():
    return {"name": "Test Deal", "price": 10000}
