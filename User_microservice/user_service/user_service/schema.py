from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Annotated,Optional
from fastapi import Form
from .utils import hash_password,verify_password 
from enum import Enum
class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    super_admin = "super_admin"  

class User(SQLModel, table=True):  # type: ignore
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", "name", name="uq_user_email_name"),)  # Enforcing unique email and name combination
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    role: RoleEnum = Field(default=RoleEnum.user) 
    
    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        return hash_password(plain_password)  
    
    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.password) 

class update_user(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str]
    role: Optional[RoleEnum]  
    
class UpdateUserRequest(BaseModel):
    name: str|None = None
    email: str|None = None
    password: str|None = None 
    

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum = RoleEnum.user  # Default to 'user'

class UserUpdate(BaseModel):
    name: str
    email: str
    role: RoleEnum
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True
        from_attributes = True 
class token(BaseModel):
    access_token: str
    token_type: str

class LoginCredentials(BaseModel):
    email: str
    password: str

    
    
