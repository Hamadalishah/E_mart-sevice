from aiokafka import AIOKafkaProducer,AIOKafkaConsumer  # type: ignore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def kafka_consumer(topic,bootstrap_servers):
    consumer = AIOKafkaConsumer(topic,bootstrap_servers=bootstrap_servers,
                                group_id="my-group",
                                auto_offset_reset="earliest",)
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Received message  {msg.value.decode()} on topic {msg.topic} partition {msg.partition} offset {msg.offset}")
    finally:
        await consumer.stop()
        

# Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()



# async def kafka_producer(topic: str, message):
#     producer = AIOKafkaProducer(bootstrap_servers='broker:19092')  # Replace with your broker address
#     await producer.start()
#     try:
#         await producer.send_and_wait(topic, message.SerializeToString())
#         print(f"Message sent to {topic}: {message}")
#     finally:
#         await producer.stop()
