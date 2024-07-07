from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
import json
import asyncio

from app.product_db import engine
from app import settings
from app.crud.crud_product import add_new_product, delete_product_by_id, get_all_products, get_product_by_id, update_product_item
from app.product_producer import get_kafka_producer, get_session
from app.models.model_product import ProductService
from app.product_consumer import consume_messages


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

             
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
    description="AI Online Mart",
    title="Welcome to Product Service",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "This is Product Service"}


@app.post("/create-new-product/", response_model=ProductService)
async def create_new_product(product: ProductService, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    product_dict = {field: getattr(product, field) for field in product.dict()}
    product_json = json.dumps(product_dict).encode("utf-8")
    print("product_JSON:", product_json)
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json)
    new_product = add_new_product(product, session)
    return new_product

@app.get("/get-product/all", response_model=list[ProductService])
def call_all_products(session: Annotated[Session, Depends(get_session)]):

    return get_all_products(session)

@app.get("/get-product/{product_id}", response_model=ProductService)
def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        return get_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/update-product/{product_id}", response_model=ProductService)
def update_single_product(product_id: int, product_data: ProductService, session: Annotated[Session, Depends(get_session)]):
    try:
        return update_product_item(product_id=product_id, product_data=product_data, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-product/{product_id}", response_model=ProductService)
def delete_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        return delete_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))