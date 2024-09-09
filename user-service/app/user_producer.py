from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app.user_db import engine
from app import settings
import json

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
    return producer 

def get_session():
    with Session(engine) as session:
        yield session

async def send_user_to_notification(id, username, recipient, subject, message):
    producer = await get_kafka_producer()
    notification_data = {
        "id": id,
        "username": username,
        "recipient": recipient,
        "subject":subject,
        "message": message
    }
    await producer.send_and_wait(settings.KAFKA_NOTIFICATION_TOPIC, json.dumps(notification_data).encode("utf-8"))
    await producer.stop()