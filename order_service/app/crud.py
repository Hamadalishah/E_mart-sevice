from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from .models import Order,OrderCreate,OrderUpdate
import asyncio
from .kafka_producer import kafka_producer
from aiokafka import AIOKafkaProducer

async def create_order_crud(order_data: OrderCreate, db: Session, producer: AIOKafkaProducer):
    new_order = Order(user_id=order_data.user_id, product_id=order_data.product_id, quantity=order_data.quantity)
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        logger.info(f"Order {new_order.order_uuid} added to the database successfully.")
        # Produce Kafka message after order creation
        await kafka_producer("order_created", f"Order created with ID: {new_order.order_uuid}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error occurred while creating order: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while creating order: " + str(e))
    return new_order

def get_order_crud(order_id: str, db: Session):
    try:
        statement = select(Order).where(Order.order_uuid == order_id)
        order = db.exec(statement).first()
        return order
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error occurred while retrieving order: " + str(e))

async def update_order_status_crud(order_id: str, status: str, db: Session, producer: AIOKafkaProducer):
    try:
        statement = select(Order).where(Order.order_uuid == order_id)
        order = db.exec(statement).first()
        if order:
            order.status = status
            db.add(order)
            db.commit()
            logger.info(f"Order {order_id} status updated to {status}")
            # Produce Kafka message after order status update
            await kafka_producer("order_updated", f"Order {order_id} updated to status: {status}")
            return order
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error occurred while updating order: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while updating order: " + str(e))

async def delete_order_crud(order_id: str, db: Session, producer: AIOKafkaProducer):
    try:
        statement = select(Order).where(Order.order_uuid == order_id)
        order = db.exec(statement).first()
        if order:
            db.delete(order)
            db.commit()
            logger.info(f"Order {order_id} deleted successfully.")
            # Produce Kafka message after order deletion
            await kafka_producer("order_deleted", f"Order {order_id} deleted successfully")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error occurred while deleting order: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while deleting order: " + str(e))