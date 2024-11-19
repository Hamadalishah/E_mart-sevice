from fastapi import FastAPI
from .rout import router as inventory_router
from .db import  create_table

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_table()

app.include_router(inventory_router, prefix="/api/v1/inventory")
