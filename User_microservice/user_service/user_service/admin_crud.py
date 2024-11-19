# crud.py
from sqlmodel import Session, select
from fastapi import HTTPException, status,Depends
from .schema import User,UserCreate,UserSchema
from .db import get_session
from typing import Annotated,List,Optional
from .crud import hash_password,db_users
from .Oauth import super_admin_required
from sqlalchemy.exc import NoResultFound
from sqlalchemy import and_,literal_column

def create_user(
    session: Annotated[Session, Depends(get_session)], user_data: UserCreate,user: Annotated[User, Depends(super_admin_required)]
):
    existing_user = db_users(session, user_data=user_data)
    if existing_user:
        return None  # Return None if email or name already exists

    # Ensure password is a valid string
    if not user_data.password:
        raise HTTPException(status_code=400, detail="Password is required")
    hashed_password = hash_password(user_data.password)  

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role="admin", 
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user


def get_all_admin_users(session: Annotated[Session, Depends(get_session)], user: User = Depends(super_admin_required)) -> List[User]:
    admin_users = list(session.exec(select(User).where(User.role == "admin")).all())
    if not admin_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No admin users found.")
    return admin_users


# Function to get admin user by ID
def get_admin_user_by_id(
    session: Annotated[Session, Depends(get_session)],
    user_id: int,
    current_user: Annotated[User, Depends(super_admin_required)]
) -> UserSchema:
    try:
        query = select(User).where(User.id == user_id)
        user = session.execute(query).scalar_one()
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found."
            )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found."
        )
    return UserSchema.from_orm(user)



def update_user_admin(
    session: Annotated[Session, Depends(get_session)],
    user_id: int,
    updated_user: User,
    current_user: Annotated[User, Depends(super_admin_required)]
) -> User:
    stmt = select(User).where(User.id == user_id)
    user = session.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update admin users.")

    update_data = updated_user.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'password': 
            value = hash_password(value)
        elif field != 'role': 
            setattr(user, field, value)
    session.commit()
    session.refresh(user)
    return user



def delete_admin_user(session: Annotated[Session, Depends(get_session)], user_id: int,current_user: Annotated[User, Depends(super_admin_required)]):
    user = session.execute(select(User).where(User.id == user_id, User.role == "admin")).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.role == "admin":
        session.delete(user)
        session.commit()
        return {"message": "Admin user deleted successfully"}

    return {"message": "User cannot be deleted. Only admins can be deleted."}
