from fastapi import APIRouter,Depends
from .db import get_session
from .scehma import UpdateProductImage
from .crudimage import add_product_image,get_image,get_single_image_by_id,update_image,delete_image
from typing import Annotated
from sqlmodel import Session
from .kafka import kafka_producer
from aiokafka import AIOKafkaProducer # type: ignore
router2 = APIRouter()


@router2.post('/image/add/{id}')
async def image_add(id:int,data:UpdateProductImage,session:Annotated[Session,Depends(get_session)],
                   producer:Annotated[AIOKafkaProducer,Depends(kafka_producer)] ):
    images= await add_product_image(id=id,data=data,session=session,producer=producer)
    return {
        f"image added succesfully{images}"
    }
    
@router2.get('/get/images{id}')
async def get_images(id:int,session:Annotated[Session,Depends(get_session)]):
    images= await get_image(id=id,session=session)
    return images

@router2.get('/get/single/image/{id1}{id2}')
async def get_single_image(id1:int,id2:int,session:Annotated[Session,Depends(get_session)]):
    images= await get_single_image_by_id(id1=id1,id2=id2,session=session)
    return images
@router2.patch('/update/image/{id1}{id2}')
async def updated_images(id1:int,id2:int,data:UpdateProductImage,session:Annotated[Session,Depends(get_session)]):
    images= await update_image(id1=id1,id2=id2,data=data,session=session)
    return {
        f"image updated succesfully{images}"
    }
    
@router2.delete('/delete/image/{id1}{id2}')
async def delete_images(id1:int,id2:int,session:Annotated[Session,Depends(get_session)]):
    delate_image = await delete_image(id1=id1,id2=id2,session=session) 
    return {
        f"image deleted succesfully{delate_image}"
    }
    
    