from app.payment_processing import process_payment_event
from aiokafka import AIOKafkaConsumer
import asyncio
import json

async def consume_payment_response_message(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="order-status-update-group",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            payment_data = json.loads(message.value.decode())
            print(f"Received payment event: {payment_data}")
            await process_payment_event(payment_data)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_payment_response_message())        