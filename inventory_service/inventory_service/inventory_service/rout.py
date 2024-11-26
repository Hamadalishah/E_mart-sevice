from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List,Annotated
from .schema import Inventory, InventoryAdd, InventoryUpdate
from .crud import (
    get_all_inventory)
from .db import get_session
# from .kafka import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession 
router = APIRouter()


@router.get("/inventory", response_model=List[Inventory])
async def get_inventories(session:Annotated[Session,Depends(get_session)]):
    result = await get_all_inventory(session)
    return result


# async def read_inventory(session: AsyncSession  = Depends(get_async_session)): 
#     inventory_data =  await get_all_inventory(session=session)
#     return inventory_data


# @router.get("/inventory/{inventory_id}", response_model=Inventory)
# async def read_inventory_item(inventory_id: int, session: Session = Depends(get_session)): 
#     inventory = await get_inventory_by_id(session, inventory_id)
#     if not inventory:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
#     return inventory


# @router.post("/inventory", response_model=Inventory)
# async def create_inventory(inventory_data: InventoryAdd, session: Session = Depends(get_session)):
#     return await add_inventory_api(session, inventory_data)


# @router.put("/inventory/{inventory_id}", response_model=Inventory)
# async def update_inventory_item(inventory_id: int, inventory_data: InventoryUpdate, session: Session = Depends(get_session)):
#     inventory = await update_inventory(session, inventory_id, inventory_data)
#     if not inventory:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
#     return inventory


# @router.delete("/inventory/{inventory_id}")
# async def delete_inventory_item(inventory_id: int, session: Session = Depends(get_session)):
#     inventory = await delete_inventory(session, inventory_id)
#     if not inventory:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
#     return {"detail": "Inventory item deleted successfully"}

