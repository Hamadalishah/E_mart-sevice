from fastapi import HTTPException,Depends,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlmodel import Session
from .db import get_session
from .schema import User
from typing import Optional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def create_access_token(data: dict, expires_delta:timedelta|None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Iska return type ko Optional[int] mein convert karte hain

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Optional[User]:
    print(f"Received token: {token}")  # Debugging: Token received
    try:
        payload = decode_jwt(token)
        print(f"Decoded payload: {payload}")  # Debugging: Check decoded payload

        user_id = payload.get("user_id")
        role = payload.get("role")
        print(f"User ID from token: {user_id}")  # Debugging: Check user_id from token
        print(f"Role from token: {role}")  # Debugging: Check role from token
        
        if user_id is None:
            print("Error: User ID is missing in the token")  # Debugging: Missing user ID
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is missing in the token")

        # Ensure user_id is an integer if it's not None
        user_id = int(user_id) if user_id is not None else None
        print(f"Converted user ID: {user_id}")  # Debugging: Check user_id conversion

        # Query to fetch user
        user = session.query(User).filter(User.id == user_id).first()
        print(f"Fetched user: {user}")  # Debugging: Check if user is fetched
        
        if user is None:
            print(f"Error: User with ID {user_id} not found")  # Debugging: User not found
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return user
    except JWTError as e:
        print(f"JWT Error: {e}")  # Debugging: Check JWT error
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
def super_admin_required(current_user: User = Depends(get_current_user)):
    print(f"Current user: {current_user}")  # Debugging line
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action. Only super admins can access this route."
        )

