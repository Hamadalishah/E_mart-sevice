from fastapi import APIRouter, Depends, HTTPException
from .Oauth import create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES
from .db import get_session
from sqlmodel import Session, select
from .schema import User
from datetime import timedelta
# from .schema import LoginCredentials
from .Oauth import super_admin_required,get_current_user
from fastapi.security import  OAuth2PasswordRequestForm
from typing import Annotated
# from .utils import auth_user


router_login = APIRouter()

@router_login.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    # Debugging: Print the email and password being processed
    print(f"Received email: {form_data.username}, password: {form_data.password}")
    
    # Fetch user from database
    statement = select(User).where(User.name == form_data.username)
    user = session.exec(statement).first()

    # Check if user exists
    if user is None:
        print("User not found.")  
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify the password
    if not user.verify_password(form_data.password):
        print("Password does not match.")  # Debugging: Password mismatch
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate access token
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Return access token
    return {"access_token": access_token, "token_type": "bearer"}

@router_login.get('/me')
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user





# @router_login.post("/token", response_model=token)
# def login_points(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
#                 session:Annotated[Session,Depends(get_session)]):
#     user = auth_user(form_data.username,form_data.password,session)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="Incorrect username or password")
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
#     return {"access_token": access_token, "token_type": "bearer"}

@router_login.get("/protected")
def get_all_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()
@router_login.delete("/delete")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


from fastapi import APIRouter, Depends

router = APIRouter()

@router_login.post("/admin-action", dependencies=[Depends(super_admin_required)])
async def perform_admin_action():
    return {"message": "This action can only be performed by a super admin"}
