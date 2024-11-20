from .scehma import Product,ProductAdd
from typing import Annotated
from sqlmodel import Session,select
from fastapi import Depends,HTTPException,status
from .db import get_session
from sqlalchemy.exc import SQLAlchemyError
from .product_pb2 import Products  # type: ignore
from .kafka import kafka_producer,serialize_product_data
import logging

logger = logging.getLogger(__name__)


async def add_product(data: Annotated[ProductAdd, Depends()],
                      session: Annotated[Session, Depends(get_session)],
                      producer):
    # Use Product model for the database
    product_db = Product(
        product_name=data.product_name,
        product_price=data.product_price,
        product_quantity=data.product_quantity,
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
        id=product_db.product_id,  # Notice we're using `product_id` from the SQLAlchemy model
        product_name=product_db.product_name,
        product_price=product_db.product_price,
        product_quantity=product_db.product_quantity,
        product_category=product_db.product_category
    )

    # Serialize and send the product data to Kafka
    serialized = serialize_product_data(product_data)
    await producer.send('product_topic', serialized)
    logger.info(f"Product added to Kafka topic: {product_data.product_name}")

    return {"Product Created Successfully": product_db}

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


async def update_product(id: int, data: ProductAdd, session: Annotated[Session, Depends(get_session)]):
    try:
        # Fetch the product based on the given ID
        product = session.exec(select(Product).where(Product.product_id == id)).one_or_none()
        
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Update the product fields (without changing the product_id)
        product.product_name = data.product_name
        product.product_price = data.product_price
        product.product_quantity = data.product_quantity
        product.product_category = data.product_category
        session.commit()
        session.refresh(product)

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Updating product error: {e}"
        )

    # Directly return the updated product object
    return product

async def delete_product(product_id:int, session: Annotated[Session, Depends(get_session)]):
    # Fetch the product to delete
    product = session.get(Product, product_id)
    if not product:
        logger.warning(f"Product with id {product_id} not found for deletion.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Create a Products message for deletion
    product_data = Products(
        id=product_id,
        product_name=product.product_name,
        product_price=product.product_price,
        product_quantity=product.product_quantity,
        product_category=product.product_category
    )
    serialized = serialize_product_data(product_data)

    async with kafka_producer() as producer:
        await producer.send('product_delete_topic', serialized)
        logger.info(f"Product deletion message sent to Kafka topic: {product_data.product_name}")

    try:
        session.delete(product)
        session.commit()
        logger.info(f"Product with id {product_id} deleted from the database successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error deleting product from the database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"deleting product error: {e}"
        )
    return {
        f"Product with id {product_id} deleted successfully"
    }

