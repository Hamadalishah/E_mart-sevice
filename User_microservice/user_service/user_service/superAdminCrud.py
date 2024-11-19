from .schema import User, RoleEnum
from .db import get_session
from .crud import hash_password
from sqlmodel import Session,text
from fastapi import Depends
from .super_admin_utlis import SUPER_ADMIN_EMAIL,SUPER_ADMIN_PASSWORD,SUPER_ADMIN_USERNAME

def initialize_super_admin() -> None:
    db: Session = next(get_session()) 
    super_admin_email = SUPER_ADMIN_EMAIL
    super_admin_name = SUPER_ADMIN_USERNAME
    super_admin_password= SUPER_ADMIN_PASSWORD 
    existing_admin = db.query(User).filter_by(email=super_admin_email).first()

    if existing_admin:
        print("Super admin already exists.")
    else:
        hashed_password = hash_password(super_admin_password) # type: ignore

        super_admin = User(
            name=super_admin_name,
            email=super_admin_email,
            password=hashed_password,
            role=RoleEnum.super_admin.value  
        )
        db.add(super_admin)
        db.commit()
        print("Super admin initialized successfully.")
    
    db.close()





def check_super_admin_exists() -> None:  
    db: Session = next(get_session()) 
    super_admin_email = "hamadexample@gmail.com"
    result = db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": super_admin_email}
    ).fetchone()

    if result:
        print("Super admin exists.")
    else:
        print("Super admin does not exist.")
    