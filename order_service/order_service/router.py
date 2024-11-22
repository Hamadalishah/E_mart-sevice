from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from .crud import create_order_crud, get_order_crud, update_order_status_crud, delete_order_crud
from .db import get_session
from aiokafka import AIOKafkaProducer
from .models import OrderCreate, OrderUpdate
import asyncio

router = APIRouter()

producer = AIOKafkaProducer(bootstrap_servers='broker:19092')  # Replace with your broker address

@router.on_event("startup")
async def startup_event():
    await producer.start()

@router.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

@router.post("/orders/")
async def create_order(order_data: OrderCreate, db: Session = Depends(get_session)):
    order = await create_order_crud(order_data, db, producer)
    return {"order_id": order.order_uuid, "status": order.status}

@router.get("/orders/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_session)):
    order = get_order_crud(order_id, db)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": order.order_uuid,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": order.status
    }

@router.put("/orders/{order_id}")
async def update_order_status(order_id: str, order_data: OrderUpdate, db: Session = Depends(get_session)):
    order = await update_order_status_crud(order_id, order_data.status, db, producer)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order.order_uuid, "new_status": order.status}

@router.delete("/orders/{order_id}")
async def delete_order(order_id: str, db: Session = Depends(get_session)):
    order = get_order_crud(order_id, db)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    await delete_order_crud(order_id, db, producer)
    return {"detail": "Order deleted successfully"}

@router.get("/health")
def health_check():
    return {"status": "Order service is running smoothly!"}