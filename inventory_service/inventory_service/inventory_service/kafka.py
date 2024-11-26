from aiokafka import AIOKafkaConsumer, AIOKafkaProducer # type: ignore
from .inventory_pb2 import Inventory  # type: ignore 
from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from .schema import Inventory
from .inventory_pb2 import Products  # type: ignore
import logging
import os
from dotenv import load_dotenv
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pydantic import ValidationError

# Load environment variables from .env file
load_dotenv()

# Update get_session to support async usage
database_url = os.getenv("DATABASEURL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")
engine = create_async_engine(database_url, echo=True, future=True)

async def get_async_session():
    async def session_generator():
        async with AsyncSession(engine) as session:
            yield session
    return session_generator()

# Create tables asynchronously
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def kafka_inventory_consumer():
    consumer = AIOKafkaConsumer(
        'product_create_topic', 
        bootstrap_servers='broker:19092', 
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

                # Use Pydantic model to validate and ignore extra fields
                try:
                    inventory_consumer_data = Inventory(
                        product_id=inventory_data.product_id,
                        product_name=inventory_data.product_name,
                        product_category=inventory_data.product_category,
                        # The rest of the fields will use default values from InventoryBase model
                    )
                except ValidationError as e:
                    logger.error(f"Validation Error: {e}")             
                    continue

                # Add inventory data to database
                async for session in get_async_session():
                    from .crud import add_inventory
                    await add_inventory(session=session, inventory_data=inventory_consumer_data.dict())

                logger.info(f"Successfully added product ID {inventory_data.product_id} to inventory.")

            except Exception as e:
                logger.error(f"Error processing message from Kafka: {e}", exc_info=True)

    finally:
        await consumer.stop()

async def add_inventory(session: AsyncSession, inventory_data: dict):
    new_inventory = Inventory(**inventory_data)  # Create Inventory instance with product data and defaults
    try:
        session.add(new_inventory)
        await session.commit()
        await session.refresh(new_inventory)
        logger.info(f"Inventory for product ID: {new_inventory.product_id} added successfully.")
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to add inventory for product ID: {inventory_data['product_id']}. Error: {e}", exc_info=True)

async def get_all_inventory():
    async with AsyncSession(engine) as session:
        statement = select(Inventory)
        results = await session.execute(statement)
        return results.scalars().all()

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    return producer

# Serialization function for Kafka messages
def serialize_inventory_data(product_data):
    return product_data.SerializeToString()