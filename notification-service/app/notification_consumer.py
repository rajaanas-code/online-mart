from aiokafka import AIOKafkaConsumer
from app.notification_producer import get_session
from app.crud.notification_crud import save_notification_to_db
import json

async def consume_messages(topic, group_id, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            notification_data = json.loads(message.value.decode('utf-8'))
            with next(get_session()) as session:
                save_notification_to_db(notification_data=notification_data, session=session)
    finally:
        await consumer.stop()

async def consume_product_messages():
    await consume_messages(
        topic='KAFKA_PRODUCT_TOPIC',
        group_id='product-group',
        bootstrap_servers='broker:19092'
    )

async def consume_order_messages():
    await consume_messages(
        topic='KAFKA_ORDER_TOPIC',
        group_id='order-group',
        bootstrap_servers='broker:19092'
    )

async def consume_user_messages():
    await consume_messages(
        topic='KAFKA_USER_TOPIC',
        group_id='user-group',
        bootstrap_servers='broker:19092'
    )

async def consume_payment_messages():
    await consume_messages(
        topic='KAFKA_PAYMENT_TOPIC',
        group_id='payment-group',
        bootstrap_servers='broker:19092'
    )
