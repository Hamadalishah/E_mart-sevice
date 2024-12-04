from fastapi import FastAPI
from .payment_routes.rout import router
from .database.db import create_table
from .paymentcrud.crud import API_KEY
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    print("Table created successfully")
    print(API_KEY)
    yield
    print("Shutting down")
    

app = FastAPI(lifespan=lifespan)



@app.get("/items/")
async def read_items():
    return [{"name": "Payment service"}]

app.include_router(router=router)
