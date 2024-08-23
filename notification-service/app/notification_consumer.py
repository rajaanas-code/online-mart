from aiokafka import AIOKafkaConsumer
import json
from app.settings import KAFKA_BROKER_URL, NOTIFICATION_TOPIC
from app.notificatio_handler import process_notification

async def consume_notification_events():
    consumer = AIOKafkaConsumer(
        NOTIFICATION_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        group_id='notification-service-group',
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            notification_data = json.loads(message.value.decode('utf-8'))
            print(f"Received notification event: {notification_data}")
            await process_notification(notification_data)
    finally:
        await consumer.stop()