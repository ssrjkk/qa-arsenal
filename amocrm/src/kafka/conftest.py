"""Kafka tests conftest."""

import pytest
from kafka import KafkaProducer, KafkaConsumer
import json


@pytest.fixture(scope="session")
def kafka_producer():
    """Kafka producer fixture."""
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092"], value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    yield producer
    producer.close()


@pytest.fixture(scope="session")
def kafka_consumer_factory():
    """Factory for creating consumers."""

    def create_consumer(topic: str, group_id: str = "test-group"):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=["localhost:9092"],
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        return consumer

    return create_consumer
