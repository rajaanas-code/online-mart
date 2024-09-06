from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session
from app.crud.order_crud import create_order, get_order_by_id
from app.model.order_model import OrderService
from app.utils.order_email import send_email
from app.order_db import engine
from contextlib import asynccontextmanager
import json
from app.order_producer import get_kafka_producer, get_session

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Welcome to Order Service",
    description="Online Mart API",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "This is Order Service"}

@app.post("/orders/", response_model=OrderService)
async def create_new_order(order: OrderService, session: Session = Depends(get_session)):
    new_order = create_order(order, session)
    
    # Send notification to Kafka
    producer = await get_kafka_producer()
    notification_data = {
        "type": "order_created",
        "message": f"Order for product ID {new_order.product_id} created successfully."
    }
    await producer.send_and_wait("notification-events", json.dumps(notification_data).encode("utf-8"))
    
    # Send email notification
    send_email(
        recipient="rajaanasturk157@gmail.com",  # Recipient email
        subject="Order Confirmation",
        message=f"Your order for product ID {new_order.product_id} has been created successfully."
    )
    
    await producer.stop()
    return new_order

@app.get("/orders/{order_id}", response_model=OrderService)
def read_order(order_id: int, session: Session = Depends(get_session)):
    return get_order_by_id(order_id, session)

