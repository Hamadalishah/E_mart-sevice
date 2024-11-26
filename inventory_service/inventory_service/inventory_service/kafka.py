from aiokafka import AIOKafkaConsumer, AIOKafkaProducer # type: ignore
from .inventory_pb2 import Inventory  # type: ignore 
from sqlmodel import select, SQLModel
from .schema import Inventory
from .inventory_pb2 import Products  # type: ignore
import logging
from .db import get_session
from sqlmodel import Session
import os
from fastapi import Depends
from typing import Annotated
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pydantic import ValidationError



async def kafka_inventory_consumer(topic,bootstrap_servers):
    consumer = AIOKafkaConsumer(
           topic, 
        bootstrap_servers=bootstrap_servers, 
        group_id="inventory-group_product_add",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            logger.info(f"Message received from Kafka: {message.value}")
            try:
                # Deserialize Protobuf data
                inventory_data = Products()  # Products Protobuf class
                inventory_data.ParseFromString(message.value)
                print(f"type of data {type(inventory_data)}")
                print(inventory_data)
                # Use Pydantic model to validate and ignore extra fields
                try:
                    inventory_consumer_data = Inventory(
                        product_id=inventory_data.product_id,
                        product_name=inventory_data.product_name,
                        product_category=inventory_data.product_category,
                        # The rest of the fields will use default values from InventoryBase model
                    )
                    print(f"inventory_consumer_data {inventory_consumer_data}")
                except ValidationError as e:
                    logger.error(f"Validation Error: {e}")             
                    continue

                # Add inventory data to database
                with next (get_session()) as session:
                    await add_inventory(session=session, inventory_data=inventory_consumer_data.dict())

                logger.info(f"Successfully added product ID {inventory_data.product_id} to inventory.")

            except Exception as e:
                logger.error(f"Error processing message from Kafka: {e}", exc_info=True)

    finally:
        await consumer.stop()

async def add_inventory(session:Annotated[Session,Depends(get_session)] ,inventory_data: dict):
    new_inventory = Inventory(**inventory_data)  
    session.add(new_inventory)
    session.commit()
    session.refresh(new_inventory)
    logger.info(f"Inventory for product ID: {new_inventory.product_id} added successfully.")

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    return producer

# Serialization function for Kafka messages
def serialize_inventory_data(product_data):
    return product_data.SerializeToString()