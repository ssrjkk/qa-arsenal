"""Test data factory for generating consistent test data."""

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import faker


class DataFactory:
    """Factory for generating test data."""

    def __init__(self, locale: str = "en_US"):
        self.faker = faker.Faker(locale)

    def random_string(self, length: int = 10, chars: str = None) -> str:
        """Generate random string."""
        if chars is None:
            chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))

    def random_email(self) -> str:
        """Generate random email."""
        return self.faker.email()

    def random_phone(self, format: str = "international") -> str:
        """Generate random phone number."""
        if format == "ru":
            return f"+7{random.randint(9000000000, 9999999999)}"
        return self.faker.phone_number()

    def random_name(self) -> str:
        """Generate random name."""
        return self.faker.name()

    def random_company(self) -> str:
        """Generate random company name."""
        return self.faker.company()

    def random_address(self) -> str:
        """Generate random address."""
        return self.faker.address()

    def random_text(self, max_chars: int = 100) -> str:
        """Generate random text."""
        return self.faker.text(max_nb_chars=max_chars)

    def random_int(self, min_val: int = 0, max_val: int = 1000) -> int:
        """Generate random integer."""
        return random.randint(min_val, max_val)

    def random_float(self, min_val: float = 0.0, max_val: float = 1000.0, decimals: int = 2) -> float:
        """Generate random float."""
        value = random.uniform(min_val, max_val)
        return round(value, decimals)

    def random_url(self) -> str:
        """Generate random URL."""
        return self.faker.url()

    def random_uuid(self) -> str:
        """Generate UUID."""
        return str(uuid.uuid4())

    def random_date(self, days_back: int = 30, format: str = "iso") -> str:
        """Generate random date."""
        date = datetime.now() - timedelta(days=random.randint(0, days_back))
        if format == "iso":
            return date.isoformat()
        return date.strftime("%Y-%m-%d")

    def random_datetime(self, days_back: int = 30, format: str = "iso") -> str:
        """Generate random datetime."""
        dt = datetime.now() - timedelta(
            days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59)
        )
        if format == "iso":
            return dt.isoformat()
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def random_choice(self, choices: List[Any]) -> Any:
        """Random choice from list."""
        return random.choice(choices)

    def random_choices(self, choices: List[Any], k: int = 2) -> List[Any]:
        """Random choices from list."""
        return random.choices(choices, k=k)


class ContactFactory(DataFactory):
    """Factory for creating contact data."""

    def create_contact(self, **overrides) -> Dict[str, Any]:
        """Create contact data."""
        contact = {
            "name": self.random_name(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "company": self.random_company(),
            "email": self.random_email(),
            "phone": self.random_phone("ru"),
            "position": self.faker.job(),
            "address": self.random_address(),
            "notes": self.random_text(max_chars=200),
        }
        contact.update(overrides)
        return contact

    def create_contact_batch(self, count: int = 5, **overrides) -> List[Dict[str, Any]]:
        """Create multiple contacts."""
        return [self.create_contact(**overrides) for _ in range(count)]


class CompanyFactory(DataFactory):
    """Factory for creating company data."""

    def create_company(self, **overrides) -> Dict[str, Any]:
        """Create company data."""
        company = {
            "name": self.random_company(),
            "email": self.random_email(),
            "phone": self.random_phone("ru"),
            "address": self.random_address(),
            "website": self.random_url(),
            "industry": self.random_choice(["IT", "Finance", "Healthcare", "Retail", "Manufacturing", "Education"]),
            "employees": self.random_int(1, 10000),
            "annual_revenue": self.random_int(100000, 100000000),
        }
        company.update(overrides)
        return company

    def create_company_batch(self, count: int = 5, **overrides) -> List[Dict[str, Any]]:
        """Create multiple companies."""
        return [self.create_company(**overrides) for _ in range(count)]


class LeadFactory(DataFactory):
    """Factory for creating lead data."""

    LEAD_STATUSES = [
        {"id": 142, "name": "Неразобранное"},
        {"id": 143, "name": "Новая заявка"},
        {"id": 144, "name": "В работе"},
        {"id": 145, "name": "Переговоры"},
        {"id": 146, "name": "Выписать счёт"},
        {"id": 147, "name": "Отправили счёт"},
        {"id": 148, "name": "Оплата"},
        {"id": 149, "name": "Успешно реализовано"},
        {"id": 150, "name": "Закрыто и не реализовано"},
    ]

    def create_lead(self, **overrides) -> Dict[str, Any]:
        """Create lead data."""
        lead = {
            "name": f"Lead from {self.random_name()}",
            "price": self.random_int(10000, 1000000),
            "status_id": self.random_choice(self.LEAD_STATUSES)["id"],
            "pipeline_id": 1,
            "tags": [self.random_string(5) for _ in range(random.randint(1, 3))],
            "notes": self.random_text(max_chars=200),
        }
        lead.update(overrides)
        return lead

    def create_lead_batch(self, count: int = 5, **overrides) -> List[Dict[str, Any]]:
        """Create multiple leads."""
        return [self.create_lead(**overrides) for _ in range(count)]


class TaskFactory(DataFactory):
    """Factory for creating task data."""

    TASK_TYPES = [
        {"id": 1, "name": "Звонок"},
        {"id": 2, "name": "Встреча"},
        {"id": 3, "name": "Написать письмо"},
        {"id": 4, "name": "Сделать действие"},
    ]

    def create_task(self, entity_id: int = 1, entity_type: str = "leads", **overrides) -> Dict[str, Any]:
        """Create task data."""
        task = {
            "task_type_id": self.random_choice(self.TASK_TYPES)["id"],
            "element_id": entity_id,
            "element_type": entity_type,
            "text": self.random_text(max_chars=100),
            "complete_till": self.random_date(days_back=7),
            "responsible_user_id": 1,
        }
        task.update(overrides)
        return task

    def create_task_batch(self, count: int = 5, **overrides) -> List[Dict[str, Any]]:
        """Create multiple tasks."""
        return [self.create_task(**overrides) for _ in range(count)]


contact_factory = ContactFactory()
company_factory = CompanyFactory()
lead_factory = LeadFactory()
task_factory = TaskFactory()
