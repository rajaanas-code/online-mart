from aiokafka import AIOKafkaConsumer
from app.models.inventory_model import InventoryItem
from app.crud.inventory_crud import create_inventory_item
from app.inventory_producer import get_session
import json

async def consume_messages(topic, bootstrap_server):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id="my-inventory",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            inventory_data = json.loads(message.value.decode())
            print(f"Inventory Data: {inventory_data}")
            with next(get_session()) as session:
                print("Saving data to database...")
                db_insert_inventory = create_inventory_item(
                    item=InventoryItem(**inventory_data), session=session)
                print("DB_INSERT_INVENTORY:", db_insert_inventory)
    finally:
        await consumer.stop()
