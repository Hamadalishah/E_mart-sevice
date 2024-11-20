from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from .schema import Inventory, InventoryAdd, InventoryUpdate
from .crud import (
    get_all_inventory,
    get_inventory_by_id,
    add_inventory,
    update_inventory,
    delete_inventory)
from .db import get_session  

router = APIRouter()


@router.get("/inventory", response_model=List[Inventory])
async def read_inventory(session: Session = Depends(get_session)): 
    return await get_all_inventory(session)


@router.get("/inventory/{inventory_id}", response_model=Inventory)
async def read_inventory_item(inventory_id: int, session: Session = Depends(get_session)): 
    inventory = await get_inventory_by_id(session, inventory_id)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return inventory


@router.post("/inventory", response_model=Inventory)
async def create_inventory(inventory_data: InventoryAdd, session: Session = Depends(get_session)):
    return await add_inventory(session, inventory_data)


@router.put("/inventory/{inventory_id}", response_model=Inventory)
async def update_inventory_item(inventory_id: int, inventory_data: InventoryUpdate, session: Session = Depends(get_session)):
    inventory = await update_inventory(session, inventory_id, inventory_data)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return inventory


@router.delete("/inventory/{inventory_id}")
async def delete_inventory_item(inventory_id: int, session: Session = Depends(get_session)):
    inventory = await delete_inventory(session, inventory_id)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return {"detail": "Inventory item deleted successfully"}

