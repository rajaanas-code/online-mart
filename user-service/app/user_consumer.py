from aiokafka import AIOKafkaConsumer
from app.crud.user_crud import UserService
from app.user_producer import get_session
from app.crud.user_crud import create_user
import json


async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-service",
        auto_offset_reset='earliest'   
    ) 
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            try:
                user_data = json.loads(message.value.decode('uft-8'))
                print("TYPE", (type(user_data)))

                with next(get_session()) as session:
                    create_user(user_data=UserService(**user_data), session=session)
            except json.JSONDecodeError:
                print("Failed to decode message, skipping...")
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        await consumer.stop()
