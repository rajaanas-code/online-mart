from aiokafka import AIOKafkaConsumer
from app.model.inventory_model import InventoryItem
from app.crud.inventory_crud import create_inventory_item
from app.inventory_producer import get_session
from app import inventory_pb2

async def consume_messages(topic, bootstrap_server):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id="inventory-service",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            # inventory_data = json.loads(message.value.decode('uft-8'))
            # print("TYPE", (type(inventory_data)))
            # print(f"Inventory Data: {inventory_data}")
            proto_item = inventory_pb2.InventoryItem()
            proto_item.ParseFromString(message.value)
            inventory_data = {
                "id": proto_item.id,
                "name": proto_item.name,
                "description": proto_item.description,
                "quantity": proto_item.quantity,
                "price": proto_item.price
            }
            print(f"Inventory Data: {inventory_data}")
            
            with next(get_session()) as session:
                print("Saving data to database...")
                db_insert_inventory = create_inventory_item(
                    item=InventoryItem(**inventory_data), session=session)
                print("DB_INSERT_INVENTORY:", db_insert_inventory)
    finally:
        await consumer.stop()