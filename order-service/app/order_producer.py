from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app import settings
from app.order_db import engine

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVERS)
    await producer.start()
    return producer

def get_session() -> Session:
    return Session(engine)