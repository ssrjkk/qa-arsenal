import uuid
import random
from typing import Any, Dict, Optional


def generate_unique_id() -> str:
    return str(uuid.uuid4())[:8]


def generate_email(domain: str = "test.com") -> str:
    return f"user_{generate_unique_id()}@{domain}"


def generate_username() -> str:
    return f"user_{generate_unique_id()}"


def generate_phone() -> str:
    return f"+7({random.randint(900, 999)}){random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"


def generate_title(prefix: str = "Test") -> str:
    return f"{prefix} {generate_unique_id()}"


def generate_body() -> str:
    words = ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit"]
    return " ".join(random.choices(words, k=random.randint(10, 30)))


def generate_name() -> str:
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_website() -> str:
    return f"www.{generate_unique_id()}.com"


class UserFactory:
    @staticmethod
    def create(**overrides) -> Dict[str, Any]:
        return {
            "name": generate_name(),
            "username": generate_username(),
            "email": generate_email(),
            "phone": generate_phone(),
            "website": generate_website(),
            **overrides
        }

    @staticmethod
    def create_with_id(user_id: int) -> Dict[str, Any]:
        data = UserFactory.create()
        data["id"] = user_id
        return data


class PostFactory:
    @staticmethod
    def create(user_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        return {
            "userId": user_id or random.randint(1, 10),
            "title": generate_title("Post"),
            "body": generate_body(),
            **overrides
        }

    @staticmethod
    def create_with_id(post_id: int) -> Dict[str, Any]:
        data = PostFactory.create()
        data["id"] = post_id
        return data


class TodoFactory:
    @staticmethod
    def create(user_id: Optional[int] = None, completed: bool = False, **overrides) -> Dict[str, Any]:
        return {
            "userId": user_id or random.randint(1, 10),
            "title": generate_title("Task"),
            "completed": completed,
            **overrides
        }

    @staticmethod
    def create_with_id(todo_id: int, **overrides) -> Dict[str, Any]:
        data = TodoFactory.create(**overrides)
        data["id"] = todo_id
        return data


class CommentFactory:
    @staticmethod
    def create(post_id: int, **overrides) -> Dict[str, Any]:
        return {
            "postId": post_id,
            "name": generate_name(),
            "email": generate_email(),
            "body": generate_body(),
            **overrides
        }


class AlbumFactory:
    @staticmethod
    def create(user_id: Optional[int] = None, **overrides) -> Dict[str, Any]:
        return {
            "userId": user_id or random.randint(1, 10),
            "title": generate_title("Album"),
            **overrides
        }


class PhotoFactory:
    @staticmethod
    def create(album_id: int, **overrides) -> Dict[str, Any]:
        return {
            "albumId": album_id,
            "title": generate_title("Photo"),
            "url": f"https://example.com/photos/{generate_unique_id()}.jpg",
            "thumbnailUrl": f"https://example.com/thumbs/{generate_unique_id()}.jpg",
            **overrides
        }


class DataBuilder:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def with_field(self, key: str, value: Any) -> "DataBuilder":
        self._data[key] = value
        return self

    def with_nested(self, key: str, data: Dict[str, Any]) -> "DataBuilder":
        self._data[key] = data
        return self

    def build(self) -> Dict[str, Any]:
        return self._data.copy()


def build_user(**kwargs) -> Dict[str, Any]:
    return DataBuilder(UserFactory.create()).with_field("custom_field", "value").build()


def build_post(**kwargs) -> Dict[str, Any]:
    return DataBuilder(PostFactory.create()).with_field("extra", "data").build()


def build_todo(**kwargs) -> Dict[str, Any]:
    return DataBuilder(TodoFactory.create()).with_field("priority", "high").build()