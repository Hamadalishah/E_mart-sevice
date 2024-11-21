from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import BaseModel


class Inventory(SQLModel, table=True):  # type: ignore
    inventory_id: Optional[int] = Field(default=None, primary_key=True)  # Primary key for inventory
    product_id: int  # Product ID to reference product information received through Kafka  # Foreign key to link with Product table
    product_name: str  # Name of the product for quick reference
    product_category: str  # Category of the product for categorization
    stock_quantity: int  # Total available quantity in inventory
    location: str  # Location in warehouse or store
    status: str = "in-stock"  # Status to indicate availability (e.g., "in-stock", "out-of-stock")
    last_modified: Optional[str]
    

class InventoryUpdate(BaseModel):
    stock_quantity: int
    location: Optional[str]
    


  
class InventoryAdd(BaseModel):
    product_id: Optional[int] 
    product: str
    stock_quantity: int  # Total available quantity in inventory
    location: str  # Location in warehouse or store
    last_restocked: Optional[str]
    

