from aiokafka import AIOKafkaConsumer # type: ignore
from .inventory_pb2 import Products  # type: ignore
from .db import get_session
from typing import Annotated
from sqlmodel import Session,select,inspect
from fastapi import Depends,HTTPException,status
from .schema import Inventory,ProductDeleteMessage
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Pydantic Model for deletion message (only product_id)

async def kafka_product_delete_consumer(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="inventory-delete-group",
        auto_offset_reset='earliest'
    )
    
    # Start the consumer
    await consumer.start()
    try:
        async for message in consumer:
            logger.info(f"Received Kafka message: {message.value}")

            try:
                # Deserialize the message from Protobuf
                try:
                    product_message = Products()
                    product_message.ParseFromString(message.value) # Use Protobuf's ParseFromString for deserialization
                    logger.info(f"Deserialized product message: {product_message}")
                    product_id = product_message.product_id
                    logger.info(f"Deserialized product_id to delete: {product_id}")
                    
                    # Perform deletion from DB (refactor this as needed)
                    with next (get_session()) as session:
                        result = delete_product_from_inventory(product_id, session)
                        logger.info(f"Deletion result: {result['message']}")
                
                except Exception as e:
                    logger.error(f"Error parsing Protobuf message: {e}")
                    continue  # Skip invalid messages

            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}", exc_info=True)
    
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped.")
        
        

# Kafka consumer function to handle product updates
async def kafka_product_update_consumer(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="inventory-update-group",
        auto_offset_reset='earliest'
    )
    
    # Start the consumer
    await consumer.start()
    try:
        async for message in consumer:
            logger.info(f"Received Kafka message: {message.value}")
            
            try:
                # Deserialize the message from Protobuf
                try:
                    product_message = Products()
                    product_message.ParseFromString(message.value)  # Deserialize the message
                    logger.info(f"Deserialized product message: {product_message}")
                    product_id = product_message.product_id
                    logger.info(f"Deserialized product_id to update: {product_id}")
                    
                   
# Inside the consumer function
                    update_data = {}
# Get all field names from Inventory model
                    inventory_fields = {field.name for field in inspect(Inventory).columns}

# Add only those fields to update_data that exist in the Inventory model
                    if product_message.product_name and 'product_name' in inventory_fields:
                        update_data['product_name'] = product_message.product_name
                    if product_message.product_category and 'product_category' in inventory_fields:
                        update_data['product_category'] = product_message.product_category
                    if product_message.last_modified and 'last_modified' in inventory_fields:
                        update_data['last_modified'] = product_message.last_modified

# Now call the update function with the filtered fields
                    with next(get_session()) as session:
                        result = update_product_in_inventory(product_id, update_data, session)
                    logger.info(f"Update result: {result['message']}")
                
                except Exception as e:
                    logger.error(f"Error parsing Protobuf message: {e}")
                    continue  # Skip invalid messages

            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}", exc_info=True)
    
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped.")
        

        
def delete_product_from_inventory(product_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        # Query the product from the inventory
        statement = session.exec(select(Inventory).where(Inventory.product_id == product_id)).first()
        if statement:
            # If product exists, delete it
            session.delete(statement)  # Delete the product from the session
            session.commit()  # Commit the transaction to the database
            logger.info(f"Successfully deleted product with ID: {product_id}")
            return {"message": f"Product with ID {product_id} deleted successfully"}
        else:
            # If product not found
            logger.warning(f"Product with ID {product_id} not found.")
            return {"message": f"Product with ID {product_id} not found."}
    except Exception as e:
        logger.error(f"Error while deleting product with ID {product_id}: {e}")
        return {"message": f"Error while deleting product with ID {product_id}"}
    
    

def update_product_in_inventory(product_id: int, data: dict, session: Session):
    try:
        # Query the product from the inventory
        statement = session.exec(select(Inventory).where(Inventory.product_id == product_id)).first()
        
        if statement:
            # If product exists, update it
            for key, value in data.items():
                setattr(statement, key, value)  # Update the attribute dynamically
            session.commit()  # Commit the transaction to the database
            logger.info(f"Successfully updated product with ID: {product_id}")
            return {"message": f"Product with ID {product_id} updated successfully"}
        else:
            # If product not found
            logger.warning(f"Product with ID {product_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found.")
    except Exception as e:
        logger.error(f"Error while updating product with ID {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while updating product with ID {product_id}: {str(e)}"
        )
# Example usage:
# bootstrap_servers: Kafka server address (e.g., "localhost:9092")
# topic: The Kafka topic to listen for messages (e.g., "product_delete_topic")
