from aiokafka import AIOKafkaProducer
import asyncio
import json
from app.settings import KAFKA_BROKER_URL, NOTIFICATION_TOPIC

async def send_notification_event(notification_data: dict):
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
    )
    await producer.start()
    try:
        await producer.send_and_wait(NOTIFICATION_TOPIC, json.dumps(notification_data).encode('utf-8'))
    finally:
        await producer.stop()