from app.stock_update import update_stock_in_inventory
from aiokafka import AIOKafkaConsumer
import json

async def consume_order_paid_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="update-stock-consumer-group",
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            order_data = json.loads(msg.value.decode())
            print(f"Received order paid event: {order_data}")
            update_stock_in_inventory(order_data)
    finally:
        await consumer.stop()