from fastapi import APIRouter,Depends,HTTPException,Form
from .db import get_session
from .scehma import ProductAdd,Product
from .crud import add_product,get_products,get_product_by_id,update_product,delete_product
from typing import Annotated
from sqlmodel import Session
from aiokafka import AIOKafkaProducer # type: ignore
from .kafka import kafka_producer
from .request import get_access_token_from_login,get_current_user
router = APIRouter()

# Login endpoint in Product Service
@router.post("/token")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    # Verify credentials and get access token from User Service
    access_token = await get_access_token_from_login(username, password)
    
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid credentials or failed to fetch token")

    return {"access_token": access_token, "token_type": "bearer"}
@router.post('/product/add')
async def product_add(product:Annotated[ProductAdd,Depends()],
                      session:Annotated[Session,Depends(get_session)],
                      producer:Annotated[AIOKafkaProducer,Depends(kafka_producer)]):
    products= await add_product(data=product,session=session,producer=producer)
    return products

@router.get('/product/get' ,dependencies=[Depends(get_current_user)])
async def product_get(session:Annotated[Session,Depends(get_session)]):
    products= await get_products(session=session)
    return products

@router.get('/single/product/{id}')
async def product_get_by_id(id:int,session:Annotated[Session,Depends(get_session)]):
    products= await get_product_by_id(id=id,session=session)
    return products

@router.put('/update/product/{id}',response_model=Product)
async def product_update(id:int,product:Annotated[ProductAdd,Depends()],session:Annotated[Session,Depends(get_session)]):
    products= await update_product(id=id,data=product,session=session)
    return products

@router.delete('/delete/product/{id}')
async def product_delete(id:int,session:Annotated[Session,Depends(get_session)]):
    products= await delete_product(product_id=id,session=session)
    return {
        f"product with id {id} deleted succesfully"
    }
