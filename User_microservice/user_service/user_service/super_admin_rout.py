from fastapi import APIRouter, Depends, HTTPException
from .db import get_session
from .schema import User
from sqlmodel import Session
from .super_admin_utlis import SUPER_ADMIN_EMAIL 
super_router = APIRouter()




@super_router.get("/check_super_admin")
async def check_super_admin(session: Session = Depends(get_session)):
    super_admin_email = SUPER_ADMIN_EMAIL
    super_admin = session.query(User).filter_by(email=super_admin_email).first()
    
    if super_admin:
        return {"message": f"Super admin {super_admin.name} exists."}
    else:
        raise HTTPException(status_code=404, detail="Super admin not found.")
