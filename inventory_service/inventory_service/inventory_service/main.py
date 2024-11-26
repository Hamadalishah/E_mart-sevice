from fastapi import FastAPI
from .rout import router as inventory_router
from .db import create_table
from .kafka import kafka_inventory_consumer
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    create_table()
    logger.info("product_create_topic")
    # Run Kafka Consumer for inventory updates and deletions
    asyncio.create_task(kafka_inventory_consumer('product_create_topic','broker:19092'))
    logger.info("Kafka consumer task started.")

app.include_router(inventory_router, prefix="/api/v1/inventory")
