from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSON
from pydantic import BaseModel
import uuid
# Define Order model using SQLModel
class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True)
    user_id: int
    product_id: int
    quantity: int
    status: str = Field(default="pending")

# Define OrderCreate model for validation
class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# Define OrderUpdate model for validation
class OrderUpdate(BaseModel):
    status: str