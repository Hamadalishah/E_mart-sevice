from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import BaseModel


class Inventory(SQLModel, table=True):  # type: ignore
    inventory_id: Optional[int] = Field(default=None, primary_key=True)  # Primary key for inventory
    product_id: int  # Product ID to reference product information received through Kafka  # Foreign key to link with Product table
    product_name: str  # Name of the product for quick reference
    product_category: str  # Category of the product for categorization
    stock_quantity: int = Field(default=0) # Total available quantity in inventory
    location: str = "out of location"  # Location in warehouse or store
    status: str = "out-of-stock" # Status to indicate availability (e.g., "in-stock", "out-of-stock")
    last_modified: Optional[str] = None
    




class InventoryBase(BaseModel):
    """Base model for Inventory"""
    product_id: int
    product_name: str
    product_category: str
    stock_quantity: int = 0  # Default value
    location: str = "default-location"  # Default value
    status: str = "in-stock"  # Default value
    last_modified: str  # Default value or Optional[str] as well if you prefer

    class Config:
        extra = "ignore"  # Ignore extra fields from Kafka message


class InventoryUpdate(BaseModel):
    stock_quantity: int
    location: Optional[str]
    


  
class InventoryAdd(BaseModel):
    product_id: Optional[int] 
    product: str
    stock_quantity: int  # Total available quantity in inventory
    location: str  # Location in warehouse or store
    last_restocked: Optional[str]

class ProductDeleteMessage(BaseModel):
    product_id: int


