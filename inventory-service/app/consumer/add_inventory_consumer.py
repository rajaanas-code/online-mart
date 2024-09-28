from app.crud.inventory_crud import add_new_inventory_item
from app.models.inventory_model import InventoryItem
from app.inventory_producer import get_session
from aiokafka import AIOKafkaConsumer
import json

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="add-inventory-consumer-group",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    try:
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")

            inventory_data = json.loads(message.value.decode())
            print("TYPE", (type(inventory_data)))
            print(f"Inventory Data {inventory_data}")

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                db_insert_product = add_new_inventory_item(
                    inventory_item_data=InventoryItem(
                        product_id=inventory_data["id"],
                        quantity=inventory_data["quantity"],
                        name=inventory_data["name"]
                    ), 
                    session=session)
                
                print("DB_INSERT_STOCK", db_insert_product)
    finally:
        await consumer.stop()