from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import BaseModel

# Database models
class Product(SQLModel, table=True):  # type: ignore
    product_id: Optional[int] = Field(default=None, primary_key=True)  # type: ignore
    product_name: str  # type: ignore
    product_price: int  # type: ignore
    product_sku: str  # type: ignore
    product_category: str  # type: ignore
    last_modified: str
    images: List["ProductImage"] = Relationship(back_populates="product")  # type: ignore
    
class ProductImage(SQLModel, table=True):  # type: ignore
    image_id: Optional[int] = Field(default=None, primary_key=True)  # type: ignore
    image_url: str  # type: ignore
    image_name: str  # type: ignore
    product_id: Optional[int] = Field(foreign_key="product.product_id")  # type: ignore
    product: Optional[Product] = Relationship(back_populates="images")  # type: ignore
 
# Request and response schemas
class ProductAdd(BaseModel):
    product_id:int
    product_name: str
    product_price: int
    product_sku: str 
    product_category: str
    last_modified: str

class ProductAddUpdate(BaseModel):
    product_name: Optional[str] = None
    product_price: Optional[int] = None
    product_sku: Optional[str] = None
    product_category: Optional[str] = None
    last_modified: Optional[str] = None

    
    
class UpdateProductImage(BaseModel):
    image_url: str
    image_name: str
    product_id: int

class LoginRequest(BaseModel):
    username: str
    password: str