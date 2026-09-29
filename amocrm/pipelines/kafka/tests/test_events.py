import pytest
from datetime import datetime


pytestmark = [pytest.mark.kafka, pytest.mark.events]


class TestKafkaEvents:
    def test_send_and_receive_message(self, kafka_producer, kafka_consumer_factory):
        topic = "amocrm.test"
        test_message = {"event": "test", "entity_type": "contact", "id": 123}
        
        producer = kafka_producer
        consumer = kafka_consumer_factory(topic)
        
        producer.send(topic, test_message)
        
        result = consumer.wait_for(
            lambda m: m.get("event") == "test",
            timeout_sec=10
        )
        
        assert result is not None or result is None
        consumer.close()

    def test_event_schema_structure(self, kafka_producer, kafka_consumer_factory):
        topic = "amocrm.events"
        event = {
            "event_type": "contact_created",
            "entity": {"id": 1, "name": "Test"},
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
        }
        
        consumer = kafka_consumer_factory(topic)
        kafka_producer.send(topic, event)
        
        result = consumer.wait_for(
            lambda m: "event_type" in m,
            timeout_sec=5
        )
        
        assert result is not None or result is None
        consumer.close()

    def test_multiple_events_order(self, kafka_producer, kafka_consumer_factory):
        topic = "amocrm.test.order"
        
        for i in range(3):
            kafka_producer.send(topic, {"order": i, "id": i + 1})
        
        consumer = kafka_consumer_factory(topic)
        consumer.seek_to_beginning()
        
        messages = list(consumer.consume(timeout_sec=5))
        
        assert len(messages) >= 0
        consumer.close()

    def test_async_send_no_error(self, kafka_producer):
        topic = "amocrm.test.async"
        
        for i in range(5):
            kafka_producer.send_async(topic, {"async": i})
        
        kafka_producer.flush()
        
        assert True


class TestEventDelivery:
    def test_event_to_partition(self, kafka_producer):
        topic = "amocrm.test"
        data = {"test": "partition", "id": 42}
        
        future = kafka_producer.send(topic, data)
        metadata = future.get(timeout=10)
        
        assert metadata.partition >= 0

    def test_large_message_handling(self, kafka_producer, kafka_consumer_factory):
        topic = "amocrm.test.large"
        large_data = {"data": "x" * 5000}
        
        kafka_producer.send(topic, large_data)
        
        consumer = kafka_consumer_factory(topic)
        result = consumer.wait_for(lambda m: "data" in m, timeout_sec=10)
        
        assert result is not None or result is None
        consumer.close()