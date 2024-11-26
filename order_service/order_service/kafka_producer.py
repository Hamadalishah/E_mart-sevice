import asyncio
from aiokafka import AIOKafkaProducer # type: ignore

# Kafka producer function
async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
        # logger.info("Kafka producer stopped")




