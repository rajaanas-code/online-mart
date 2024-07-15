from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app.order_db import engine
from app.settings import BOOTSTRAP_SERVERS

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

def get_db():
    with Session(engine) as session:
        yield session
