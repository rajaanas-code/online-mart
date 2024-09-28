from app.models.product_model import Product,ProductUpdate
from app.crud.product_crud import add_new_product
from app.product_producer import get_session
from aiokafka import AIOKafkaConsumer
from app import settings
import json

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
        auto_offset_reset='earliest'
    )

    await consumer.start()
    try:
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")

            product_data = json.loads(message.value.decode())
            print("TYPE", (type(product_data)))
            print(f"Product Data {product_data}")

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                db_insert_product = add_new_product(
                    product_data=Product(**product_data), session=session)
                print("DB_INSERT_PRODUCT", db_insert_product)
                
            print(f"Received message: {message.value.decode()} on topic {message.topic}")
    finally:
        await consumer.stop()