import json
import logging
from kafka import KafkaProducer as _KafkaProducer
from kafka import KafkaConsumer as _KafkaConsumer
from config.settings import KAFKA_BROKERS
from typing import Callable, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaProducerClient:
    def __init__(self, brokers: list = None, serializer: str = "json"):
        self.brokers = brokers or KAFKA_BROKERS
        self.serializer = serializer
        self._producer = None

    def _get_producer(self):
        if not self._producer:
            self._producer = _KafkaProducer(
                bootstrap_servers=self.brokers,
                value_serializer=self._serialize,
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
            )
        return self._producer

    def _serialize(self, value):
        if self.serializer == "json":
            return json.dumps(value).encode("utf-8")
        return value

    def send(self, topic: str, value: dict, key: str = None):
        logger.info(f"Sending to {topic}: {value}")
        future = self._get_producer().send(topic, value=value, key=key)
        return future.get(timeout=10)

    def send_async(self, topic: str, value: dict, key: str = None):
        return self._get_producer().send(topic, value=value, key=key)

    def flush(self):
        if self._producer:
            self._producer.flush()

    def close(self):
        if self._producer:
            self._producer.close()


class KafkaConsumerClient:
    def __init__(
        self,
        topic: str,
        brokers: list = None,
        group_id: str = "test-consumer",
        offset_reset: str = "latest",
        deserializer: str = "json",
    ):
        self.topic = topic
        self.brokers = brokers or KAFKA_BROKERS
        self.group_id = group_id
        self.offset_reset = offset_reset
        self.deserializer = deserializer
        self._consumer = None

    def _get_consumer(self):
        if not self._consumer:
            self._consumer = _KafkaConsumer(
                self.topic,
                bootstrap_servers=self.brokers,
                group_id=self.group_id,
                auto_offset_reset=self.offset_reset,
                value_deserializer=self._deserialize,
                enable_auto_commit=True,
            )
        return self._consumer

    def _deserialize(self, value):
        if self.deserializer == "json":
            return json.loads(value.decode("utf-8"))
        return value

    def consume(self, timeout_ms: int = 5000, max_records: int = 1):
        return self._get_consumer().poll(timeout_ms=timeout_ms, max_records=max_records)

    def wait_for(
        self,
        predicate: Callable[[dict], bool],
        timeout_sec: int = 30,
        poll_interval: float = 0.5,
    ) -> Optional[dict]:
        start = time.time()
        while time.time() - start < timeout_sec:
            records = self.consume()
            for partition, messages in records.items():
                for msg in messages:
                    if predicate(msg.value):
                        return msg.value
            time.sleep(poll_interval)
        return None

    def close(self):
        if self._consumer:
            self._consumer.close()


class KafkaClient:
    def __init__(self, brokers: list = None):
        self.brokers = brokers or KAFKA_BROKERS
        self._producer = None
        self._consumers = {}

    @property
    def producer(self):
        if not self._producer:
            self._producer = KafkaProducerClient(self.brokers)
        return self._producer

    def consumer(self, topic: str, group_id: str = None):
        key = f"{topic}:{group_id}"
        if key not in self._consumers:
            self._consumers[key] = KafkaConsumerClient(topic, self.brokers, group_id)
        return self._consumers[key]

    def create_topic(self, topic: str, partitions: int = 1, replication: int = 1):
        logger.info("Topic creation not implemented - using auto-create")

    def close(self):
        if self._producer:
            self._producer.close()
        for consumer in self._consumers.values():
            consumer.close()
