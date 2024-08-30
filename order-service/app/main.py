from aiokafka import AIOKafkaProducer
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel
from contextlib import asynccontextmanager
import asyncio
import json

from app.order_db import engine
from app.order_producer import get_db
from app.model.order_model import Order, OrderItem
from app.crud.order_crud import create_order_item, get_order_item_from_db, update_order_in_db, delete_order_from_db, add_order_item_to_db, get_order_from_db
from app.order_producer import get_kafka_producer
from app.settings import KAFKA_ORDER_TOPIC
from app.order_consumer import consume_order_messages


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables...")
    task = asyncio.create_task(consume_order_messages())
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Order Service",
    description="AI Online Mart",
    version="0.0.1",
)



@app.get("/")
def read_root():
    return {"Hello": "This is Order Service"}


@app.post("/create-order/", response_model=Order)
async def create_order(order: Order, db: Session = Depends(get_db), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    order_dict = order.dict()
    order_json = json.dumps(order_dict).encode("utf-8")
    await producer.send_and_wait(KAFKA_ORDER_TOPIC, order_json)
    return create_order_item(db=db, order=order)


@app.get("/get-order/{order_id}", response_model=Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    try:
        return get_order_from_db(db=db, order_id=order_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update-order/{order_id}", response_model=Order)
def update_order(order_id: int, order: Order, db: Session = Depends(get_db)):
    try:
        return update_order_in_db(db=db, order_id=order_id, order=order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-order/{order_id}", response_model=Order)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    try:
        return delete_order_from_db(db=db, order_id=order_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-order-item/{order_id}/items/", response_model=OrderItem)
def add_order_item(order_id: int, item: OrderItem, db: Session = Depends(get_db)):
    return add_order_item_to_db(db=db, order_id=order_id, item=item)


@app.get("/get-order-item/{order_id}/items/", response_model=list[OrderItem])
def get_order_item(order_id: int, db: Session = Depends(get_db)):
    return get_order_item_from_db(db=db, order_id=order_id)