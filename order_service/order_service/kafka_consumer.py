import asyncio
from aiokafka import AIOKafkaConsumer # type:ignore

async def consume_order_events():
    consumer = AIOKafkaConsumer(
        'order_topic',
        bootstrap_servers='broker:9092',
        group_id="order_group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received order: {message.value.decode('utf-8')}")
    finally:
        await consumer.stop()
