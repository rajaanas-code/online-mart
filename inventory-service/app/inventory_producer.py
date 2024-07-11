from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app.inventory_db import engine
from app import settings
import inventory_pb2

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

def serialize_inventory_items(item):
    proto_item = inventory_pb2.InventoryItem(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity
    )
    return proto_item.SerializeToString()