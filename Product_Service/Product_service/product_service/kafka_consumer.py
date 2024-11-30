from aiokafka import AIOKafkaProducer,AIOKafkaConsumer  # type: ignore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def kafka_consumer_delete_product(topic,bootstrap_servers):
    consumer = AIOKafkaConsumer(topic,bootstrap_servers=bootstrap_servers,
                                group_id="my-product-delete-group",
                                auto_offset_reset="earliest",)
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Received message  {msg.value.decode()} on topic {msg.topic} partition {msg.partition} offset {msg.offset}")
    finally:
        await consumer.stop()
        