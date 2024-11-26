from fastapi import FastAPI
from .router import router # type: ignore
from .db import create_table # type: ignore
from contextlib import asynccontextmanager

# Assuming create_table is an async function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan event started.")
    print("Creating table...")
    create_table()  # Await this since it's async
    print("Table created successfully.")
    yield
    print("Lifespan event ended.")

# Passing the lifespan parameter while instantiating FastAPI
app = FastAPI(lifespan=lifespan)
app.include_router(router)
