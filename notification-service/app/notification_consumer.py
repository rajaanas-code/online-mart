from aiokafka import AIOKafkaConsumer
from app.crud.notification_crud import save_notification_to_db
from app.notification_producer import get_session
import json
from app import settings

async def consume_notification_messages():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_NOTIFICATION_TOPIC,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id="notification-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            notification_data = json.loads(message.value.decode('utf-8'))
            print(f"Received message: {notification_data}")
            with next(get_session()) as session:
                save_notification_to_db(notification_data=notification_data, session=session)
    finally:
        await consumer.stop()