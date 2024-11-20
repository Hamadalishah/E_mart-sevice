from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import BaseModel

class Inventory(SQLModel, table=True): # type: ignore
    inventory_id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] 
    product_name: str
    stock_quantity: int 
    product_category: str
    

class InventoryUpdate(BaseModel):
    stock_quantity: int
    location: Optional[str]
    


  
class InventoryAdd(BaseModel):
    product_id: Optional[int] 
    product: str
    stock_quantity: int  # Total available quantity in inventory
    location: str  # Location in warehouse or store
    last_restocked: Optional[str]
    

