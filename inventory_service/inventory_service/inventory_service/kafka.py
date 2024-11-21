from aiokafka import AIOKafkaConsumer, AIOKafkaProducer # type: ignore
from .inventory_pb2 import Inventory  # type: ignore 
from sqlmodel import select
from .db import get_session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def kafka_inventory_consumer():
    consumer = AIOKafkaConsumer(
        'product_create_topic', 'product_update_topic', 'product_delete_topic',
        bootstrap_servers='localhost:9092', group_id="inventory-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = product_pb2.ProductMessage()
            message.ParseFromString(msg.value)
            if msg.topic == 'product_create_topic':
                # Add inventory entry for the new product
                await handle_add_inventory(message)
            elif msg.topic == 'product_update_topic':
                # Update inventory details based on product changes
                await handle_update_inventory(message)
            elif msg.topic == 'product_delete_topic':
                # Delete inventory entry for the product
                await handle_delete_inventory(message)
    finally:
        await consumer.stop()

async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
        logger.info("Kafka producer stopped")

# Serialization function for Kafka messages
def serialize_inventory_data(product_data):
    return product_data.SerializeToString()


        
