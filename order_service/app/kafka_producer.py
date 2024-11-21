import asyncio
from aiokafka import AIOKafkaProducer

# Kafka producer function
async def kafka_producer(topic: str, message):
    producer = AIOKafkaProducer(bootstrap_servers='localhost:19092')  # Replace with your broker address
    await producer.start()
    try:
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logger.info(f"Message sent to {topic}: {message}")
    finally:
        await producer.stop()



