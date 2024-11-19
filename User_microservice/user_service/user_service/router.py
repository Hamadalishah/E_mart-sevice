from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from .crud import create_user, get_user_by_id, update_user, delete_user, get_all_users
from .db import get_session
from .schema import User, UserCreate, UserUpdate
from .Oauth import get_current_user # Import the new dependency

user_router = APIRouter()

@user_router.post("/users", response_model=User)
async def create_users(user: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, user)

@user_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Fetch user by ID
    db_user = get_user_by_id(session, user_id,current_user=current_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Allow a user to view their own profile or admin can view any user
    if current_user.id != user_id and current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="You can only view your own profile.")
    
    return db_user
@user_router.put("/users/{user_id}")
async def update_user_by_id(
    user_id: int,
    update_data: User,  # Assuming User schema is used for validation
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # Call the update_user function from crud.py
        updated_user = update_user(session, user_id, update_data, current_user)
        return {"message": "User details updated successfully", "user": updated_user}
    except HTTPException as e:
        raise e
@user_router.delete("/users/{user_id}")
async def delete_user_by_id(
    user_id: int, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    # Ensure that only the user can delete their own account or an admin can delete any user
    if current_user.id != user_id and current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="You can only delete your own account or an admin can delete any account.")
    
    db_user = get_user_by_id(session, user_id,current_user=current_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {'message' : 'User deleted successfully'}

@user_router.get("/users", response_model=list[User])
async def get_all_users_(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Fetching all users (only for super admin)
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="you are not eligible to view all users.")    
    return get_all_users(session,current_user=current_user)
