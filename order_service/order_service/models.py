from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from enum import Enum
from typing import Optional

# Enum for order status
class OrderStatus(str, Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"




class DeliveryAddress(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int  # Foreign key to link this address to the user
    country: str
    state: str
    city: str
    address: str  
    
    
class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    product_id: int
    quantity: int
    status: OrderStatus = Field(default=OrderStatus.pending)
    address_id: int = Field(default=None, foreign_key="address.id")




class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    address_id: int  # Use address_id from the Address model

# Define OrderUpdate model for validation
class OrderUpdate(BaseModel):
    status: Optional[OrderStatus]
    quantity: Optional[int]
