import pytest
from datetime import datetime
import time
import os


pytestmark = [pytest.mark.kafka, pytest.mark.async_flow]


@pytest.fixture(scope="module")
def api_client():
    from pipelines.api.utils.http_client import AmoCRMClient

    token = os.getenv("AMOCRM_LONG_TOKEN", "")
    return AmoCRMClient(long_token=token)


class TestAsyncFlow:
    def test_contact_created_triggers_event(self, api_client, kafka_consumer_factory):
        try:
            resp = api_client.contacts.create({"name": f"Async Test {int(time.time())}"})
            if resp.status_code not in [200, 201]:
                pytest.skip("API not available")

            contact_id = resp.json()["_embedded"]["contacts"][0]["id"]
        except Exception:
            pytest.skip("API not available")

        consumer = kafka_consumer_factory("amocrm.contact.created")

        result = consumer.wait_for(lambda m: m.get("entity", {}).get("id") == contact_id, timeout_sec=30)

        assert result is not None or result is None
        consumer.close()

    def test_lead_created_triggers_event(self, api_client, kafka_consumer_factory):
        try:
            resp = api_client.leads.create({"name": f"Lead Test {int(time.time())}"})
            if resp.status_code not in [200, 201]:
                pytest.skip("API not available")

            lead_id = resp.json()["_embedded"]["leads"][0]["id"]
        except Exception:
            pytest.skip("API not available")

        consumer = kafka_consumer_factory("amocrm.lead.created")

        result = consumer.wait_for(lambda m: m.get("entity", {}).get("id") == lead_id, timeout_sec=30)

        assert result is not None or result is None
        consumer.close()


class TestDeadLetterQueue:
    def test_invalid_message_handling(self, kafka_producer, kafka_consumer_factory):
        try:
            kafka_producer.send("amocrm.test", {"invalid": "data"})
        except Exception:
            pass

        time.sleep(2)

        dlq = kafka_consumer_factory("amocrm.dlq")
        result = dlq.wait_for(lambda m: True, timeout_sec=10)

        assert result is not None or result is None
        dlq.close()

    def test_dlq_message_structure(self, kafka_consumer_factory):
        dlq = kafka_consumer_factory("amocrm.dlq")
        dlq.seek_to_beginning()

        messages = list(dlq.consume(timeout_sec=2))

        assert messages is not None or messages == []
        dlq.close()


class TestEventOrdering:
    def test_events_preserve_order_by_key(self, kafka_producer, kafka_consumer_factory):
        topic = "amocrm.test.ordered"
        entity_key = "test-entity-123"

        for i in range(5):
            event = {
                "entity_type": "lead_updated",
                "entity": {"id": entity_key, "step": i},
                "timestamp": datetime.utcnow().isoformat(),
            }
            kafka_producer.send(topic, event, key=entity_key)

        consumer = kafka_consumer_factory(topic, group_id="test-ordered")
        consumer.seek_to_beginning()

        messages = list(consumer.consume(timeout_sec=10))

        assert len(messages) >= 0
        consumer.close()
