from aiokafka import AIOKafkaConsumer
from app.settings import BOOTSTRAP_SERVERS, KAFKA_ORDER_TOPIC
from app.order_db import engine
from app.models.model import Order
from app.crud.crud import create_order
import json
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def consume_messages():
    consumer = AIOKafkaConsumer(
        KAFKA_ORDER_TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="order-service",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            order_data = json.loads(message.value.decode('utf-8'))
            order = Order(**order_data)
            with SessionLocal() as session:
                create_order(db=session, order=order)
    finally:
        await consumer.stop()
