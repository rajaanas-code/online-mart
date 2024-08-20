from aiokafka import AIOKafkaProducer
from sqlalchemy import create_engine
from sqlmodel import Session
from app.settings import settings
import json

# Initialize Kafka Producer
async def get_kafka_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.BOOTSTRAP_SERVER
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

# Provide database session
async def get_session() -> Session:
    engine = create_engine(str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg2"))
    async with Session(engine) as session:
        yield session

async def send_payment_event(payment_event: dict):
    async for producer in get_kafka_producer():
        message = json.dumps(payment_event).encode('utf-8')
        await producer.send_and_wait(settings.KAFKA_PAYMENT_TOPIC, message)
