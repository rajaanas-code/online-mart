from app.models.order_model import Order
from aiokafka import AIOKafkaProducer
from sqlmodel import Session, select
from app.order_db import engine
import json

async def process_payment_event(payment_data):
    with Session(engine) as session:
        order = session.exec(select(Order).where(Order.id == payment_data["order_id"])).one_or_none()
        if order:
            order.status = "Paid"
            session.add(order)
            session.commit()
            session.refresh(order)
            event = {
                "order_id": order.id,
                "product_id": order.product_id,
                "quantity": order.quantity,
                "status": "Paid"
            }
            await produce_event("order_paid", event)


async def produce_event(topic, event):
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        await producer.send_and_wait(topic, json.dumps(event).encode('utf-8'))
        print(f"Produced event to {topic}: {event}")
    finally:
        await producer.stop()           