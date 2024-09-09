from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app import settings
from app.order_db import engine
import json

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVERS)
    await producer.start()
    return producer

def get_session() -> Session:
    return Session(engine)

async def send_order_to_notification(id, product_id, quantity, amount, message, recipient, subject):
    producer = await get_kafka_producer()
    notification_data = {
        "id": id,
        "product_id": product_id,
        "quantity": quantity,
        "amount": amount,
        "message": message,
        "recipient": recipient,
        "subject":subject
    }
    await producer.send_and_wait(settings.KAFKA_NOTIFICATION_TOPIC, json.dumps(notification_data).encode("utf-8"))
    await producer.stop()