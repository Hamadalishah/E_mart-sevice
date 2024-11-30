from fastapi import FastAPI
from .payment_routes.rout import router
from .database.db import create_table




app = FastAPI()
app.on_event("startup")
def on_startup():
    create_table()
    print("Table created successfully")
    


@app.get("/items/")
async def read_items():
    return [{"name": "Payment service"}]

app.include_router(router=router)
