from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id
from app.product_producer import get_kafka_producer, get_session 
from app.model.product_model import ProductService
from app.product_db import engine
from contextlib import asynccontextmanager
import json

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Welcome to Product Service",
    description="Online Mart API",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "This is Product Service"}

@app.post("/products/", response_model=ProductService)
async def create_product(product: ProductService, session: Session = Depends(get_session)):
    new_product = add_new_product(product, session)
    
    # Send notification to Kafka
    producer = await get_kafka_producer()
    notification_data = {
        "type": "product_created",
        "message": f"Product {new_product.name} created successfully."
    }
    await producer.send_and_wait("notification-events", json.dumps(notification_data).encode("utf-8"))
    await producer.stop() 
    return new_product

@app.get("/products/", response_model=list[ProductService])
def read_products(session: Session = Depends(get_session)):
    return get_all_products(session)

@app.get("/products/{product_id}", response_model=ProductService)
def read_product(product_id: int, session: Session = Depends(get_session)):
    return get_product_by_id(product_id, session)