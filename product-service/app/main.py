from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
import json

from app.product_db import engine
from app.crud.product_crud import add_new_product, delete_product_by_id, get_all_products, get_product_by_id, update_product_item
from app.product_producer import get_kafka_producer, get_session
from app.model.product_model import ProductService

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="Product Service")

@app.post("/products-create/", response_model=ProductService)
async def create_product(product: ProductService, session: Session = Depends(get_session)):
    new_product = add_new_product(product, session)
    # Send notification to Kafka
    producer = await get_kafka_producer()
    notification_data = {
        "type": "product_created",
        "message": f"Product {new_product.name} created successfully."
    }
    await producer.send_and_wait("notification-events", json.dumps(notification_data).encode("utf-8"))
    return new_product

@app.get("/products/", response_model=list[ProductService])
def read_products(session: Session = Depends(get_session)):
    return get_all_products(session)

@app.get("/products-get/{product_id}", response_model=ProductService)
def read_product(product_id: int, session: Session = Depends(get_session)):
    return get_product_by_id(product_id, session)
    
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