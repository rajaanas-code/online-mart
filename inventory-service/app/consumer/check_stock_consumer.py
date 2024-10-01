from app.models.inventory_model import InventoryItem
from app.inventory_producer import get_session
from aiokafka import AIOKafkaConsumer
from aiokafka import AIOKafkaProducer
from sqlmodel import select
import json

async def consume_order_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="check-inventory-stock",
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            order_data = json.loads(message.value.decode())
            
            print("TYPE", (type(order_data)))
            print(f"Order Data {order_data}")

            with next(get_session()) as session:
                try:
                    inventory_item = session.exec(select(InventoryItem).where(InventoryItem.product_id == order_data["product_id"])).one_or_none()
                    if inventory_item and inventory_item.quantity >= order_data["quantity"]:
                        response = {"order_id": order_data["id"], "status": "success", "order": order_data}
                        print("status : success")
                    else:
                        response = {"order_id": order_data["id"], "status": "failed", "order": order_data}
                        print("status : failed")
                except Exception as e:
                    response = {"order_id": order_data["id"], "status": "error", "detail": str(e), "order": order_data}
                    
            response_json = json.dumps(response).encode("utf-8")
            producer = AIOKafkaProducer(
                        bootstrap_servers='broker:19092')
            await producer.start()
            try:
                await producer.send_and_wait(
                    "order-check-response",
                    response_json
                )
            finally:
                await producer.stop()
    finally:
        await consumer.stop()