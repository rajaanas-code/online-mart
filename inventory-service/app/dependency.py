from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app.inventory_db import engine
from app import settings

async def get_kafka_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.BOOTSTRAP_SERVER
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

def get_session():
    with Session(engine) as session:
        yield session