from .scehma import Product,ProductAdd
from typing import Annotated
from sqlmodel import Session,select
from fastapi import Depends,HTTPException,status
from .db import get_session
from sqlalchemy.exc import SQLAlchemyError
from .product_pb2 import Products  # type: ignore
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer  # type: ignore
from .kafka import get_kafka_producer
import logging

logger = logging.getLogger(__name__)

async def add_product(data: Annotated[Products, Depends()],
                      session: Annotated[Session, Depends(get_session)],
                      producer:Annotated[AIOKafkaProducer, Depends(get_kafka_producer)] ):
    # Use Product model for the database
    product_db = Product(
        product_name=data.product_name,
        product_price=data.product_price,
        product_sku=data.product_sku,
        product_category=data.product_category
    )

    try:
        # Insert the product into the database
        session.add(product_db)
        session.commit()
        session.refresh(product_db)
        logger.info(f"Product {product_db.product_name} added to the database successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error adding product to the database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"adding product error: {e}"
        )

    # Create a Products Protobuf message for Kafka serialization
    product_data = Products(
        product_id=product_db.product_id,  # Notice we're using `product_id` from the SQLAlchemy model
        product_name=product_db.product_name,
        product_price=product_db.product_price,
        product_sku=product_db.product_sku,
        product_category=product_db.product_category
    )
    serialized_product = product_data.SerializeToString()
    await producer.send('product_create_topic', serialized_product,key=str(product_db.product_id).encode('utf-8'))



async def get_products(session:Annotated[Session,Depends(get_session)]):
    try:
        products = session.exec(select(Product)).all()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting products error: {e}"
        )
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
            )
    return {
        "Product" : products
    }
    
    
async def get_product_by_id(id:int,session:Session):
    try:
        product = session.exec(select(Product).where(Product.product_id == id)).first()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product error: {e}"
        )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
            )
    return {
        "Product" : product
    }
    
# async def update_product(
#     id: int,
#     data: ProductAdd,
#     session: Session,
#     producer: AIOKafkaProducer
# ):
#     try:
#         # Fetch and update product in the database
#         product = session.exec(select(Product).where(Product.product_id == id)).first()
#         if not product:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

#         # Update only fields that are provided in the request
#         updated_fields = {}
#         if data.product_name is not None:
#             product.product_name = data.product_name
#             updated_fields['product_name'] = data.product_name
#         if data.product_price is not None:
#             product.product_price = data.product_price
#             updated_fields['product_price'] = data.product_price
#         if data.product_quantity is not None:
#             product.product_quantity = data.product_quantity
#             updated_fields['product_quantity'] = data.product_quantity
#         if data.product_category is not None:
#             product.product_category = data.product_category
#             updated_fields['product_category'] = data.product_category

#         # Commit changes to the database
#         session.commit()
#         session.refresh(product)
#         logger.info(f"Product {product.product_name} updated successfully.")

#     except SQLAlchemyError as e:
#         session.rollback()
#         logger.error(f"Error updating product: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"updating product error: {e}"
#         )

#     # Serialize the updated fields as a Protobuf message and send to Kafka
#     product_data = Products(
#         product_id=product.product_id,
#         product_name=product.product_name,
#         product_price=product.product_price,
#         product_quantity=product.product_quantity,
#         product_category=product.product_category
#     )

#     serialized_data = product_data.SerializeToString()
#     await producer.send_and_wait('product_update_topic', serialized_data)

#     return product

# async def delete_product(product_id: int, session: Annotated[Session, Depends(get_session)], producer:Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
#     try:
#         # Fetch and delete product from the database
#         product = session.exec(select(Product).where(Product.product_id == product_id)).first()
#         if not product:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

#         session.delete(product)
#         session.commit()
#         logger.info(f"Product {product.product_name} deleted successfully.")
#     except SQLAlchemyError as e:
#         session.rollback()
#         logger.error(f"Error deleting product: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"deleting product error: {e}"
#         )

#     # Create and serialize a Protobuf message for deletion and send to Kafka
#     product_message = Products(
#         product_id=product_id
#     )
#     serialized_data = product_message.SerializeToString()
#     await producer('product_delete_topic', serialized_data)

