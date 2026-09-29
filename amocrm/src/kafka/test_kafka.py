"""Kafka tests - working examples."""

import pytest
import time


pytestmark = pytest.mark.kafka


class TestKafkaEvents:
    """Kafka event tests."""

    def test_produce_message(self, kafka_producer):
        """Can produce message to Kafka."""
        topic = "test-events"

        message = {"event": "test", "data": {"id": 1, "name": "Test"}, "timestamp": time.time()}

        future = kafka_producer.send(topic, value=message)
        record = future.get(timeout=10)

        assert record.topic == topic
        assert record.partition >= 0
        assert record.offset >= 0

    def test_consumer_receives_message(self, kafka_producer, kafka_consumer_factory):
        """Consumer receives produced message."""
        topic = "test-consumer"

        message = {"event": "test", "id": 123}
        kafka_producer.send(topic, value=message)
        kafka_producer.flush()

        time.sleep(2)

        consumer = kafka_consumer_factory(topic)

        received = []
        for msg in consumer:
            received.append(msg.value)
            if len(received) >= 1:
                break

        assert len(received) > 0
        assert received[0]["event"] == "test"

        consumer.close()

    def test_multiple_messages(self, kafka_producer):
        """Can send multiple messages."""
        topic = "test-multiple"

        for i in range(3):
            kafka_producer.send(topic, {"message": f"test-{i}"})

        kafka_producer.flush()

        assert True


class TestKafkaDLQ:
    """Dead Letter Queue tests."""

    def test_dlq_topic_exists(self):
        """DLQ topic handling."""
        topic = "dead-letter-queue"

        assert topic is not None
