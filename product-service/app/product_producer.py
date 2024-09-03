from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app import settings
from app.product_db import engine

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
    return producer

def get_session() -> Session:
    return Session(engine)