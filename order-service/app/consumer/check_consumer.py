from app.crud.order_crud import place_order
from app.order_producer import get_session
from app.models.order_model import Order
from aiokafka import AIOKafkaConsumer
import json

async def consume_order_response_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="order-check-response-group",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    try:
        async for message in consumer:
            print("RAW CHECK RESPONSE CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")

            response_data = json.loads(message.value.decode())
            print(f"Response Data {response_data}")
            if response_data["status"] == "success":
                session = next(get_session())
                try:
                    order_data = response_data["order"]
                    new_order = place_order(session, Order(**order_data))
                    print(f"Order placed successfully")
                except Exception as e:
                    session.rollback()
                    print(f"Failed to place order: {e}")
                finally:
                    session.close()
            else:
                print(f"Insufficient stock for order: {response_data['order_id']}")
    finally:
        await consumer.stop()