from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import Session, SQLModel
from typing import AsyncGenerator
from typing import Annotated
import asyncio

from app import settings
from app.inventory_db import engine
from app.inventory_producer import get_session
from app.consumer.add_inventory_consumer import consume_messages
from app.consumer.check_stock_consumer import consume_order_messages
from app.models.inventory_model import InventoryItem, InventoryItemUpdate
from app.consumer.update_stock_consumer import consume_order_paid_messages
from app.authentication.auth import admin_required, LoginForAccessTokenDep
from app.crud.inventory_crud import delete_inventory_item_by_id, get_all_inventory_items, get_inventory_item_by_id, update_inventory_by_id

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating table..")
    task = asyncio.create_task(consume_messages("product-events",settings.BOOTSTRAP_SERVER))
    asyncio.create_task(consume_order_messages(
    "order_placed",
    settings.BOOTSTRAP_SERVER
    ))

    asyncio.create_task(consume_order_paid_messages(
    "order_paid",
    settings.BOOTSTRAP_SERVER
    ))

    print("refresh")
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Inventory Service",
    description="Online Mart API",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"message": "This is Inventory Service"}

@app.post("/auth/login")
def login(token:LoginForAccessTokenDep):
    return token

@app.get("/manage-inventory/all", response_model=list[InventoryItem],dependencies=[Depends(admin_required)])
def all_inventory_items(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_all_inventory_items(session)


@app.get("/manage-inventory/{item_id}", response_model=InventoryItem,dependencies=[Depends(admin_required)])
def single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single inventory item by ID"""
    try:
        return get_inventory_item_by_id(inventory_item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/manage-inventory/{item_id}", response_model=dict,dependencies=[Depends(admin_required)])
def delete_single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single inventory item by ID"""
    try:
        return delete_inventory_item_by_id(inventory_item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/manage-inventory/{product_id}", response_model=InventoryItemUpdate,dependencies=[Depends(admin_required)])
def update_single_inventory_item(product_id: int, item: InventoryItemUpdate, session: Annotated[Session, Depends(get_session)]):
    """ Update a single inventory item by ID"""
    try:
        return update_inventory_by_id(product_id=product_id, update_product_inventory=item, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))