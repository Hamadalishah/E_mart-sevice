from aiokafka import AIOKafkaProducer,AIOKafkaConsumer  # type: ignore





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
        
        
        
async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
