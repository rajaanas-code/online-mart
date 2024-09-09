from fastapi import HTTPException 
from sqlmodel import Session, select
from app.models.inventory_model import InventoryItem


def create_inventory_item(item: InventoryItem, session:Session):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def get_all_inventory_item(session:Session):
    return session.exec(select(InventoryItem)).all()

def get_inventory_item(item_id: int, session: Session):
    item = session.exec(select(InventoryItem).where(InventoryItem.id == item_id)).first()
    if item is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Item id {item_id} not found!"
        )
    return item

def update_inventory_item(item_id: int, item_data: InventoryItem, session: Session):
    item = session.exec(select(InventoryItem).where(InventoryItem.id == item_id)).first()
    if item:
        for key, value in item_data.dict(exclude_unset=True).items():
            setattr(item, key, value)
        session.commit()
        session.refresh(item)
        return item
    raise HTTPException(
        status_code=404, 
        detail=f"Item {item_id} is not found"
    )
    
def delete_inventory_item(item_id: int, session: Session):
    item = session.exec(select(InventoryItem).where(InventoryItem.id == item_id)).first()
    if item:
        session.delete(item)
        session.commit()
        return{"message" : f"Item {item_id} is deleted succesfully"}
    raise HTTPException(
        status_code=404,
        detail=f"Item {item_id} is not found"
    )




