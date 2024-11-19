from passlib.exc import UnknownHashError
from passlib.context import CryptContext
from fastapi import Depends
from typing import Annotated
from sqlmodel import Session,select
from .db import get_session



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password,password):
    try:
        
        return pwd_context.verify(plain_password,password)
    except UnknownHashError:
        print("Password hash could not be identified.")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# def db_user(session: Annotated[Session, Depends(get_session)],
#                    username: str | None = None,
#                    email: str | None = None):
#     from .schema import User
#     statement = select(User).where(User.name == username)
#     user = session.exec(statement).first()
    
#     if not user:
#         statement = select(User).where(User.email == email)
#         user = session.exec(statement).first()
        
#     return user

# def auth_user(username:str| None ,password:str,
#                      session: Annotated[Session, Depends(get_session)]
#                                     ):
#     data_user = db_user(session=session,username=username)
#     if not data_user:
#         return False
#     if not verify_password(password,data_user.password):
#         return False
#     return data_user