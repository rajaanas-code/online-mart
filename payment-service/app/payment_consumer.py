from aiokafka import AIOKafkaConsumer
from app.crud.payment_crud import add_payment
from app.model.payment_model import Payment
from app.payment_producer import get_session
import json
from app import settings

async def consume_payment_messages():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_PAYMENT_TOPIC,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id="payment-group",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            payment_data = json.loads(message.value.decode('utf-8'))
            with next(get_session()) as session:
                add_payment(payment_data=Payment(**payment_data), session=session)
    finally:
        await consumer.stop()