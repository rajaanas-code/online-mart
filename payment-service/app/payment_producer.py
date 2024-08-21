from aiokafka import AIOKafkaProducer
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlmodel import Session

async def get_kafka_producer() -> AsyncGenerator[AIOKafkaProducer, None]:
    from app.settings import settings
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.BOOTSTRAP_SERVER
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

async def get_session() -> AsyncGenerator[Session, None]:
    from app.settings import settings 
    engine = create_engine(str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg2"))
    async with Session(engine) as session:
        yield session
