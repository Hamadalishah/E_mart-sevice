# router.py
from fastapi import APIRouter, Depends,HTTPException,status
from sqlmodel import Session
from .db import get_session
from .schema import User,UserCreate
from .admin_crud import create_user,get_all_admin_users, get_admin_user_by_id, update_user_admin,delete_admin_user
from typing import Annotated,List
from .Oauth import super_admin_required
admin_route = APIRouter()

@admin_route.post("/admin/users", response_model=User)
async def create_admin(user:UserCreate,session:Annotated[Session,Depends(get_session)],current_user:Annotated[User,Depends(super_admin_required)]):
    admin_user =  create_user(session, user,user=current_user)
    return admin_user

@admin_route.get("/admin")
async def admin():
    return {"message": "Welcome to the admin page!"}

@admin_route.get("/admin/users", response_model=List[User])
async def get_all_admin_users_endpoint(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(super_admin_required)]) -> List[User]:
    admin_users = get_all_admin_users(session=session, user=current_user)
    return admin_users

@admin_route.get("/admin/users/{user_id}", response_model=User)
async def get_admin_by_id(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(super_admin_required)]):
    try:
        admin_user = get_admin_user_by_id(session, user_id=user_id, current_user=current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}")
    
@admin_route.put("/admin/users/{user_id}", response_model=User)
async def update_admin(
    user_id: int,
    updated_user: User,
    session: Session = Depends(get_session),
    current_user: User = Depends(super_admin_required)
):
    try:
        # Call the function to update the admin user
        updated_admin = update_user_admin(session, user_id, updated_user, current_user=current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
    return updated_admin

@admin_route.delete("/admin/users/{user_id}")
async def delete_admin(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(super_admin_required)]):
    try:
        response = delete_admin_user(session, user_id,current_user=current_user)
        return response
    except HTTPException as e:
        raise e  # Propagate specific HTTPException errors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )