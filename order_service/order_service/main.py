from fastapi import FastAPI
from .router import router
from .db import crate_table
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifspan event is started")
    print("table creating....")
    create_table()
    print("table created succesfully")
    yield
    
app = FastAPI()
app.include_router(router)