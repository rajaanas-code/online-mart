from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
import asyncio

from app.db import engine
from app import settings
from app.crud.crud_product import add_new_product, delete_product_by_id, get_all_products, get_product_by_id
from app.dpdcy import get_kafka_producer, get_session
from app.models.model_product import ProductService


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


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

             

# Lifespan Function
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")

    task = asyncio.create_task(consume_messages(
        settings.KAFKA_PRODUCT_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield

# FastAPI app instance
app = FastAPI(
    lifespan=lifespan,
    title="Hello this is Product Service",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "PanaCloud"}


@app.post("/manage-products/", response_model=ProductService)
async def create_new_product(product: ProductService, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):

    product_dict = {field: getattr(product, field) for field in product.dict()}
    product_json = json.dumps(product_dict).encode("utf-8")
    print("product_JSON:", product_json)
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json)
    new_product = add_new_product(product, session)
    return new_product

@app.get("/manage-products/all", response_model=list[ProductService])
def call_all_products(session: Annotated[Session, Depends(get_session)]):

    return get_all_products(session)

@app.get("/manage-products/{product_id}", response_model=ProductService)
def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):

    try:
        return get_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/manage-products/{product_id}", response_model=ProductService)
def delete_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):


    try:
        return delete_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))