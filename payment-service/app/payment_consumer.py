from aiokafka import AIOKafkaConsumer
from app.crud.payment_crud import add_payment
from app.model.payment_model import Payment
from app.payment_producer import get_session
import json

async def consume_payment_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
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
