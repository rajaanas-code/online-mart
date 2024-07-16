from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel
from contextlib import asynccontextmanager
import asyncio
import json

from app.order_db import engine
from app.models.model import Order, OrderItem
from app.crud import crud
from app import settings
from app.order_producer import get_kafka_producer
from app.settings import KAFKA_ORDER_TOPIC
from app.order_consumer import consume_messages


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")

    task = asyncio.create_task(consume_messages(
        settings.KAFKA_ORDER_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    description="AI Online Mart",
    title="Order Service",
    version="0.0.1",
)



@app.get("/")
def read_root():
    return {"Hello": "This is Order Service"}


def get_db():
    with Session(engine) as session:
        yield session


@app.post("/orders/", response_model=Order)
async def create_order(order: Order, db: Session = Depends(get_db), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    order_dict = order.dict()
    order_json = json.dumps(order_dict).encode("utf-8")
    await producer.send_and_wait(KAFKA_ORDER_TOPIC, order_json)
    return crud.create_order(db=db, order=order)


@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    try:
        return crud.read_order(db=db, order_id=order_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, order: Order, db: Session = Depends(get_db)):
    try:
        return crud.update_order(db=db, order_id=order_id, order=order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/orders/{order_id}", response_model=Order)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_order(db=db, order_id=order_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders/{order_id}/items/", response_model=OrderItem)
def add_order_item(order_id: int, item: OrderItem, db: Session = Depends(get_db)):
    return crud.add_order_item(db=db, order_id=order_id, item=item)


@app.get("/orders/{order_id}/items/", response_model=list[OrderItem])
def read_order_item(order_id: int, db: Session = Depends(get_db)):
    return crud.read_order_item(db=db, order_id=order_id)
