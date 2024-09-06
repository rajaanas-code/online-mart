from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session
from app.crud.payment_crud import add_payment, get_payment_by_order
from app.payment_db import engine
from contextlib import asynccontextmanager
from app.payment_producer import get_kafka_producer, get_session
from app.model.payment_model import Payment
from app.utils.payment_email import send_email
import json

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Welcome to Payment Service",
    description="Online Mart API",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "This is Payment Service"}

@app.post("/payments/", response_model=Payment)
async def create_new_payment(payment: Payment, session: Session = Depends(get_session)):
    new_payment = add_payment(payment, session)
    
    # Send notification to Kafka
    producer = await get_kafka_producer()
    notification_data = {
        "type": "payment_processed",
        "message": f"Payment of {new_payment.amount} for order ID {new_payment.order_id} processed successfully."
    }
    await producer.send_and_wait("notification-events", json.dumps(notification_data).encode("utf-8"))
    
    # Send email notification
    send_email(
        recipient="rajaanasturk157@gmail.com",  # Recipient email
        subject="Payment Confirmation",
        message=f"Your payment of ${new_payment.amount} for order ID {new_payment.order_id} has been completed successfully."
    )
    
    # await producer.stop()
    return new_payment

@app.get("/payments/order/{order_id}", response_model=Payment)
def read_payment(order_id: int, session: Session = Depends(get_session)):
    return get_payment_by_order(order_id, session)