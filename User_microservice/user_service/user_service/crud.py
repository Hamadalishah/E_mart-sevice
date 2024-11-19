from sqlmodel import Session, select
from .schema import User, UserCreate
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from .db import get_session
from passlib.exc import UnknownHashError
from typing import Annotated, Optional
from .Oauth import get_current_user  # Import the dependency for getting current user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Verify password using the hashing algorithm
def verify_password(plain_password, password):
    try:
        return pwd_context.verify(plain_password, password)
    except UnknownHashError:
        print("Password hash could not be identified.")

# Hash the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Check if a user with the same name or email already exists
def db_users(session: Annotated[Session, Depends(get_session)], user_data: UserCreate) -> Optional[User]:
    statement = select(User).where((User.name == user_data.name) | (User.email == user_data.email))
    user = session.exec(statement).first()  # Execute the statement properly
    
    if user is None:
        return None 
    return user

# Create a new user with role 'user' and password hashing
def create_user(session: Annotated[Session, Depends(get_session)], user_data: UserCreate):
    existing_user = db_users(session, user_data=user_data)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    if not user_data.password:
        raise HTTPException(status_code=400, detail="Password is required")
    hashed_password = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role="user",  # Default role as 'user'
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

# Get user by ID
def get_user_by_id(session: Annotated[Session, Depends(get_session)], user_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    return session.exec(select(User).where(User.id == user_id)).first()

# Get all users
def get_all_users(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]):
    return session.exec(select(User)).all()



def update_user(
    session: Session, 
    user_id: int, 
    update_data: User, 
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    user_to_update = get_user_by_id(session, user_id,current_user=current_user)
    if user_to_update is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user_id and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="You can only update your own account")
    if update_data.name is not None:
        user_to_update.name = update_data.name
    if update_data.email is not None:
        user_to_update.email = update_data.email
    if update_data.password is not None:
        user_to_update.password = hash_password(update_data.password)
    session.commit()
    session.refresh(user_to_update)
    
    return user_to_update

def delete_user(
    session: Annotated[Session, Depends(get_session)], 
    user_id: int, 
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Ensure that the current user can only delete their own account, or an admin or super admin can delete users
    if current_user.id != user_id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="You can only delete your own account, or an admin can delete users.")
    
    user_to_delete = get_user_by_id(session, user_id, current_user=current_user)
    
    if user_to_delete is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Admins can only delete users, not other admins or super admins
    if current_user.role == "admin" and user_to_delete.role != "user":
        raise HTTPException(status_code=403, detail="Admins can only delete users.")

    # Super admins can only delete users with the role "user", not other admins or super admins
    if current_user.role == "super_admin" and user_to_delete.role != "user":
        raise HTTPException(status_code=403, detail="Super admins can only delete users.")

    # Proceed with the deletion
    session.delete(user_to_delete)
    session.commit()

    return {"message": "User deleted successfully"}
