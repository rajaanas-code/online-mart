from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app import settings
from app.payment_db import engine
import json 

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
    return producer

def get_session() -> Session:
    return Session(engine) 

async def send_payment_to_notification(id, order_id, amount, recipient, subject, message):
    producer = await get_kafka_producer()
    notification_data = {
        "id": id,
        "order_id": order_id,
        "amount": amount,
        "recipient": recipient,
        "subject":subject,
        "message": message
    }
    await producer.send_and_wait(settings.KAFKA_NOTIFICATION_TOPIC, json.dumps(notification_data).encode("utf-8"))
    await producer.stop()