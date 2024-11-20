from aiokafka import AIOKafkaConsumer, AIOKafkaProducer # type: ignore
from .inventory_pb2 import Inventory  # type: ignore 
from sqlmodel import select
from .db import get_session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def kafka_inventory_consumer(topic, delete_topic, bootstrap_servers, update_product_topic):
    consumer = AIOKafkaConsumer(
        topic, delete_topic, update_product_topic,
        bootstrap_servers=bootstrap_servers,
        group_id="inventory-group",
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    await consumer.start()
    logger.info("Kafka consumer started and listening to inventory topics.")
    try:
        async for msg in consumer:
            # Deserialize the inventory data
            inventory_data = Inventory()
            inventory_data.ParseFromString(msg.value)

            # Extract inventory details
            product_id = inventory_data.product_id
            product_name = inventory_data.product_name
            stock_quantity = inventory_data.stock_quantity

            # Handle the different topics
            async with get_session() as session:
                if msg.topic == topic:
                    # Handle add/update inventory messages
                    inventory_item = session.exec(select(Inventory).where(Inventory.product_id == product_id)).one_or_none()
                    if inventory_item:
                        inventory_item.stock_quantity = stock_quantity
                        session.commit()
                        logger.info(f"Inventory updated for product: {product_name}")
                    else:
                        # Add new inventory item if it doesn't exist
                        new_inventory = Inventory(
                            product_id=product_id,
                            product=product_name,
                            stock_quantity=stock_quantity,
                            location="Default Warehouse"
                        )
                        session.add(new_inventory)
                        session.commit()
                        logger.info(f"New inventory item added for product: {product_name}")
                elif msg.topic == delete_topic:
                    # Handle delete inventory messages
                    inventory_item = session.exec(select(Inventory).where(Inventory.product_id == product_id)).one_or_none()
                    if inventory_item:
                        session.delete(inventory_item)
                        session.commit()
                        logger.info(f"Inventory item deleted for product: {product_name}")
    finally:
        await consumer.stop()
        await producer.stop()
        logger.info("Kafka consumer stopped.")
        
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


        
