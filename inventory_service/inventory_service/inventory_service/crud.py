from sqlmodel import Session, select
from .schema import Inventory, InventoryAdd, InventoryUpdate

# Get all inventory items
async def get_all_inventory(session: Session):
    statement = select(Inventory)
    results = session.exec(statement).all()
    return results

# Get inventory item by ID
async def get_inventory_by_id(session: Session, inventory_id: int):
    return session.get(Inventory, inventory_id)

# Add a new inventory item
async def add_inventory(session: Session, inventory_data: InventoryAdd):
    new_inventory = Inventory(**inventory_data.dict())
    session.add(new_inventory)
    session.commit()
    session.refresh(new_inventory)
    return new_inventory

# Update an existing inventory item
async def update_inventory(session: Session, inventory_id: int, inventory_data: InventoryUpdate):
    inventory = await get_inventory_by_id(session, inventory_id)
    if inventory:
        for key, value in inventory_data.dict(exclude_unset=True).items():
            setattr(inventory, key, value)
        session.commit()
        session.refresh(inventory)
    return inventory

# Delete an inventory item
async def delete_inventory(session: Session, inventory_id: int):
    inventory = await get_inventory_by_id(session, inventory_id)
    if inventory:
        session.delete(inventory)
        session.commit()
    return inventory
