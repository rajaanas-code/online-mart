from app.crud.notification_crud import add_new_notification
from app.models.notification_model import Notification
# from app.send_email import send_email_notification
from app.notification_producer import get_session
from aiokafka import AIOKafkaConsumer
import json

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-consumer-group",
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")

            notification_data = json.loads(message.value.decode())
            print(f"Notification Data: {notification_data}")

            with next(get_session()) as session:
                print("Saving data to database")
                db_insert_notification = add_new_notification(
                    notification_data=Notification(**notification_data), session=session)
                print("DB_INSERT_NOTIFICATION", db_insert_notification)
            #Send email notification
            # if 'recipient' in notification_data:
            #         send_email_notification(
            #             email_to=notification_data['recipient'],
            #             subject=notification_data['title'],
            #             email_content_for_send=notification_data['message']
            #         )
    finally:
        
        await consumer.stop()