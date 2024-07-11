from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
import asyncio

# import json
from app.inventory_db import engine
from app import settings
from app.inventory_producer import get_session, get_kafka_producer
from app.models.inventory_model import InventoryItem
from app.crud.inventory_crud import create_inventory_item, get_inventory_item, delete_inventory_item, get_all_inventory_item, update_inventory_item
from app.inventory_consumer import consume_messages


""" Function to create the database table """
def create_db_table() -> None:
    SQLModel.metadata.create_all(engine)
    

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("creating table..")
    task = asyncio.create_task(consume_messages(
        settings.KAFKA_INVENTORY_TOPIC, 'broker:19092'))
    create_db_table()
    yield


""" Initialize FastAPI app """
app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Inventory Service",
    description="AI Online Mart",
    version="0.0.1",
)
            
""" Root endpoint """
@app.get("/")
def read_root():
    return {"Hello": "This is Inventory Service"}

""" Endpoint to create a new inventory item """
@app.post("/create-inventory/", response_model=InventoryItem)
async def create_new_inventory_item(item: InventoryItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Convert item to JSON  """
    # item_dict = {field: getattr(item, field) for field in item.dict()}
    # item_json = json.dumps(item_dict).encode("utf-8")
    proto_item = InventoryItem(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity,
    )
    item_bytes = proto_item.SerializeToString()
    print("Sending item data to kafka:" ,item_bytes)
    await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, item_bytes)
    new_item = create_inventory_item(item, session)
    return new_item


""" Endpoint to get all inventory items """
@app.get("/get-all-inventory/", response_model=list[InventoryItem])
def call_all_inventory_items(session: Annotated[Session, Depends(get_session)]):
    return get_all_inventory_item(session)


""" Endpoint to get a single inventory item by ID """
@app.get("/get-inventory/{item_id}", response_model=InventoryItem)
def get_single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        return get_inventory_item(item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

""" Endpoint to update an inventory item by ID """
@app.put("/update-inventory/{item_id}", response_model=InventoryItem)
async def update_single_inventory_item(item_id: int, item_data: InventoryItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    # try:
    #     return update_inventory_item(item_id=item_id, item_data=item_data, session=session)
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    proto_item = InventoryItem(
        id=item_data.id,
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
        quantity=item_data.quantity
    )
    item_bytes = proto_item.SerializeToString()
    print("Sending update item data to kafka:", item_bytes)
    await producer.send_wait(settings.KAFKA_INVENTORY_TOPIC, item_bytes)
    update_item = update_inventory_item(item_id=item_id, item_data=item_data, session=session)
    return update_item

""" Endpoint to delete an inventory item by ID """
@app.delete("/delete-inventory/{item_id}", response_model=dict)
def delete_single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        return delete_inventory_item(item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
