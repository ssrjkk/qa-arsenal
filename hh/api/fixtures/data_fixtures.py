import json
from pathlib import Path
from typing import Any, Dict, cast

from utils.logger import logger


def load_test_data() -> Dict[str, Any]:
    data_file = Path(__file__).parent.parent / "data" / "test_data.json"

    if data_file.exists():
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                return cast(Dict[str, Any], json.load(f))
        except json.JSONDecodeError as error:
            logger.warning(f"Failed to parse test_data.json: {error}")

    return {
        "search_queries": {
            "valid": [
                "QA engineer",
                "Python developer",
                "DevOps",
            ],
            "invalid": [
                "",
                "   ",
                "x" * 500,
            ],
        },
        "areas": {
            "spb": "2",
            "moscow": "1",
            "ekb": "3",
        },
        "vacancy_test_data": {
            "valid_per_page_values": [5, 10, 20, 50, 100],
            "max_per_page": 100,
        },
        "expected_response_times": {
            "vacancies_search": 3000,
            "areas": 2000,
            "dictionaries": 1500,
        },
    }


TEST_DATA = load_test_data()
