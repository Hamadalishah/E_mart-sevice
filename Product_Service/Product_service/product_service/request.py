from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status,Depends,HTTPException
import httpx
import logging

# logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     url = "http://user_service:8000/token"

#     data = {
#         "username": form_data.username,
#         "password": form_data.password
#     }
    
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, data=data)
        
#     if response.status_code == 200:
#         return response.json()["access_token"]  
    
#     raise HTTPException(status_code=response.status_code, detail=f"{response.text}")
# import httpx

async def get_access_token_from_login(username: str, password: str):
    login_url = "http://user_service:8000/token"
    form_data = {
        "username": username,
        "password": password
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(login_url, data=form_data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise HTTPException(status_code=response.status_code, detail=f"{response.text}")# Function to get current user from user service
# async def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]):
#     user_service_url = "http://user-service:8000/me"  # Adjust URL for user service
    
#     # Sending token in the Authorization header
#     headers = {"Authorization": f"Bearer {token}"}
    
#     async with httpx.AsyncClient() as client:
#         response = await client.get(user_service_url, headers=headers)
    
#     if response.status_code != 200:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
#     return response.json()
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    logging.info(f"Received token: {token}")
    url = "http://user_service:8000/me"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(
        status_code=response.status_code,
        detail="Could not validate credentials"
    )

async def check_user_role(token: str):
    user_data = await get_current_user(token)
    role = user_data.get("role")  # Assuming role is in the response data
    
    # Check if the user is 'admin' or 'super admin'
    if role not in ['admin', 'super admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
    
    return user_data


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     logging.info(token)
    
#     print("Received token:", token)  # Debug print
#     url = "http://user_service:8000/get_user"  # URL to the user service
#     headers = {"Authorization": f"Bearer {token}"}
#     print("Sending request to user service with headers:", headers)

#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
        
#         print("Request headers:", headers)
#         print("Response status code:", response.status_code)  # Debug print
#         return response.json()
        

# from fastapi import HTTPException, status, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy.future import select
# from sqlalchemy.exc import NoResultFound
# from sqlalchemy import or_
# from pydantic import BaseModel
# from typing import Annotated
# import httpx
# import logging

# # SQLAlchemy session dependency
# def get_session():
#     # Replace this with the actual session code for your application.
#     pass
# def super_admin_required(current_user: dict = Depends(get_current_user)):
#     # Replace this with actual super admin validation code
#     if current_user.get("role") != "super_admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You are not authorized to perform this action. Only super admins can access this route."
#         )

# # Example User model
# class User:
#     id: int
#     name: str
#     email: str
#     role: str

# # Pydantic schema for response
# class UserSchema(BaseModel):
#     id: int
#     name: str
#     email: str
#     role: str

#     class Config:
#         orm_mode = True
#         from_attributes = True

# # Function to get admin user by ID
# def get_admin_user_by_id(
#     session: Annotated[Session, Depends(get_session)],
#     user_id: int,
#     current_user: Annotated[dict, Depends(super_admin_required)]
# ) -> UserSchema:
#     try:
#         # SQLAlchemy query to find admin user by ID
#         query = select(User).where(User.id == user_id)
#         user = session.execute(query).scalar_one()

#         # Check if the user is an admin
#         if user.role != "admin":
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Admin user not found."
#             )
#     except NoResultFound:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Admin user not found."
#         )

#     # Return the user as a UserSchema
#     return UserSchema.from_orm(user)

# # Function to get the current user from the token
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
#     logging.info(f"Received token: {token}")
#     url = "http://user_service:8000/get_user"
#     headers = {"Authorization": f"Bearer {token}"}
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     raise HTTPException(
#         status_code=response.status_code,
#         detail="Could not validate credentials"
#     )
