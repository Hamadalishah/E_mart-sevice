from sqlalchemy.ext.asyncio import AsyncSession
from .schema import Inventory, InventoryAdd, InventoryUpdate
# from .kafka import kafka_producer,serialize_inventory_data # Import Kafka producer and serializer
from typing import Annotated
from fastapi import Depends
from .db import get_session
import logging
 
from sqlmodel import Session ,select

logger = logging.getLogger(__name__)

# Get all inventory items

async def get_all_inventory(session: AsyncSession):
    statement = select(Inventory)
    results = await session.execute(statement)
    return results.scalars().all()
# Get inventory item by ID
async def get_inventory_by_id(session: Session, inventory_id: int):
    return session.get(Inventory, inventory_id)

# Function to add inventory to the database
async def add_inventory(session:Annotated[Session, Depends(get_session)], inventory_data: dict):
    new_inventory = Inventory(**inventory_data)  # Create Inventory instance with product data and defaults
    try:
        session.add(new_inventory)
        session.commit()
        session.refresh(new_inventory)
        logger.info(f"Inventory for product ID: {new_inventory.product_id} added successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to add inventory for product ID: {inventory_data['product_id']}. Error: {e}")

# Run the consumer
# asyncio.run(consume_product_updates())


# # Add a new inventory item
# async def add_inventory_api(session: Session, inventory_data: InventoryAdd):
#     new_inventory = Inventory(**inventory_data.dict())
#     session.add(new_inventory)
#     session.commit()
#     session.refresh(new_inventory)
    
#     # Serialize the data and send to Kafka
#     serialized = serialize_inventory_data(new_inventory)
#     async with kafka_producer as producer:
#         await producer.send('inventory_update_topic', serialized)
#         logger.info(f"Inventory added to Kafka topic for product ID: {new_inventory.product_id}")

#     return new_inventory

# # Update an existing inventory item
# async def update_inventory(session: Session, inventory_id: int, inventory_data: InventoryUpdate):
#     inventory = await get_inventory_by_id(session, inventory_id)
#     if inventory:
#         for key, value in inventory_data.dict(exclude_unset=True).items():
#             setattr(inventory, key, value)
#         session.commit()
#         session.refresh(inventory)

#         # Serialize the data and send to Kafka
#         serialized = serialize_inventory_data(inventory)
#         async with kafka_producer as producer:
#             await producer.send('inventory_update_topic', serialized)
#             logger.info(f"Inventory updated in Kafka topic for product ID: {inventory.product_id}")

#     return inventory

# # Delete an inventory item
# async def delete_inventory(session: Session, inventory_id: int):
#     inventory = await get_inventory_by_id(session, inventory_id)
#     if inventory:
#         session.delete(inventory)
#         session.commit()
#         serialized = serialize_inventory_data(inventory)
#         async with kafka_producer as producer:
#             await producer.send('inventory_delete_topic', serialized)
#             logger.info(f"Inventory deletion sent to Kafka topic for product ID: {inventory.product_id}")

#     return inventory
