from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer
import json
import asyncio
import json

from app.inventory_db import engine
from app import settings
from app.dependency import get_session, get_kafka_producer
from app.models.inventory_model import InventoryItem
from app.crud.inventory_crud import create_inventory_item, get_inventory_item, delete_inventory_item, get_all_inventory_item, update_inventory_item


def create_db_table() -> None:
    SQLModel.metadata.create_all(engine)
    

async def consume_messages(topic, bootstrap_server):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id="my-inventory",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            inventory_data = json.loads(message.value.decode())
            print(f"Inventory Data: {inventory_data}")
            with next(get_session()) as session:
                print("Saving data to database...")
                db_insert_inventory = create_inventory_item(
                    item=InventoryItem(**inventory_data), session=session)
                print("DB_INSERT_INVENTORY:", db_insert_inventory)
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("creating table..")
    task = asyncio.create_task(consume_messages(
        settings.KAFKA_INVENTORY_TOPIC, 'broker:19092'))
    create_db_table()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Inventory Service",
    description="AI Online Mart",
    version="0.0.1",
)
            

@app.get("/")
def read_root():
    return {"Hello": "This is Inventory Service"}

@app.post("/create-inventory/", response_model=InventoryItem)
async def create_new_inventory_item(item: InventoryItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    item_dict = {field: getattr(item, field) for field in item.dict()}
    item_json = json.dumps(item_dict).encode("utf-8")
    print("Item json:" ,item_json)
    await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, item_json)
    new_item = create_inventory_item(item, session)
    return new_item

@app.get("/get-all-inventory/", response_model=list[InventoryItem])
def call_all_inventory_items(session: Annotated[Session, Depends(get_session)]):
    return get_all_inventory_item(session)


@app.get("/get-inventory/{item_id}", response_model=InventoryItem)
def get_single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        return get_inventory_item(item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update-inventory/{item_id}", response_model=InventoryItem)
def update_single_inventory_item(item_id: int, item_data: InventoryItem, session: Annotated[Session, Depends(get_session)]):
    try:
        return update_inventory_item(item_id=item_id, item_data=item_data, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-inventory/{item_id}", response_model=dict)
def delete_single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        return delete_inventory_item(item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))                                    