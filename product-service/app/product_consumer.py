from aiokafka import AIOKafkaConsumer
from app.models.model_product import ProductService
from app.crud.crud_product import add_new_product
from app.product_producer import get_session
import json


async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-product",
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")

            product_data = json.loads(message.value.decode())
            print("TYPE", (type(product_data)))
            print(f"Product Data", {product_data})

            with next(get_session()) as session:
                print("SAVING DATA TO DATABASE")
                db_insert_product = add_new_product(
                    product_data=ProductService(**product_data), session=session)
                print("DB_INSERT_PRODUCT", db_insert_product)
    finally:
        await consumer.stop()