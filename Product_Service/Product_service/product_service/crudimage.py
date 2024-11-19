from .scehma import Product, ProductImage,UpdateProductImage
from typing import Annotated
from sqlmodel import Session,select
from fastapi import Depends,HTTPException,status
from .db import get_session
from sqlalchemy.exc import SQLAlchemyError
from .product_pb2 import ProductImages  # type: ignore
from aiokafka import AIOKafkaProducer # type: ignore
from .kafka import kafka_producer


async def add_product_image(id:int, data:UpdateProductImage,session:Annotated[Session,Depends(get_session)],
                           producer:Annotated[AIOKafkaProducer,Depends(kafka_producer)] ):
    
    try:
        product = session.exec(select(Product).where(Product.product_id == id)).one()
        new_image = ProductImage(image_url=data.image_url,image_name=data.image_name,product_id=product.product_id)
        producer_data = ProductImages(product_id=product.product_id,image_url=data.image_url,image_name=data.image_name)
        serialized = producer_data.SerializeToString()
        await producer.send("product_image",serialized)
        session.add(new_image)
        session.commit()
        session.refresh(new_image)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"updating product image error: {e}"
        )
    return {"message": "Product image created succesfully successfully",
            "image_id": new_image.image_id}
    
async def get_image(id:int,session:Annotated[Session,Depends(get_session)]):
    try:
        check_product_id = session.exec(select(ProductImage).where(ProductImage.product_id == id)).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product image error: {e}"
        )
    if check_product_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image not found"
        )
        
    try:
        images = session.exec(select(ProductImage).where(ProductImage.product_id==id)).all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product image error: {e}"
        )
    return images

async def get_single_image_by_id(id1:int,id2:int,session:Annotated[Session,Depends(get_session)]):
    try:
        image = session.exec(select(ProductImage).where(ProductImage.product_id==id1,ProductImage.image_id==id2)).one()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product image error: {e}"
        )
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image not found"
        )
    return {"image_id": image}
    
async def update_image(id1:int,id2:int,data:UpdateProductImage,session:Annotated[Session,Depends(get_session)]):
    try:
        image = session.exec(select(ProductImage).where(ProductImage.product_id==id1,ProductImage.image_id==id2)).one()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product image error: {e}"
        )
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image not found"
        )
    image.image_name = data.image_name
    image.image_url = data.image_url
    image.product_id = data.product_id
    session.add(image)
    session.commit()
    session.refresh(image)
    return {"message": "Image updated successfully",
            "image_id": image}

async def delete_image(id1:int,id2:int,session:Annotated[Session,Depends(get_session)]):
    try:
        image = session.exec(select(ProductImage).where(ProductImage.product_id==id1,ProductImage.image_id==id2)).one()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product image error: {e}"
        )
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image not found"
        )
    session.delete(image)
    session.commit()
    return {"message": "Image deleted successfully",
            "image_id": image}
