from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app import settings
from app.user_db import engine
import json

async def get_kafka_producer():
    """Create and return a Kafka producer."""
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
    return producer

def get_session() -> Session:
    """Get a new database session."""
    return Session(engine)

async def send_user_data_to_payment_service(user_data: dict):
    """Send user data to the payment service via Kafka."""
    producer = await get_kafka_producer()
    
    # Prepare the message payload
    message_payload = {
        "username": user_data["username"],
        "email": user_data["email"],
        "hashed_password": user_data["hashed_password"]  # Only include if necessary; consider security.
    }
    
    # Send the message to the Kafka topic for user events
    await producer.send_and_wait(settings.KAFKA_USER_TOPIC, json.dumps(message_payload).encode("utf-8"))
    
    # Stop the producer after sending the message
    await producer.stop()