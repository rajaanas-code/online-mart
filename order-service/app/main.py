from fastapi import FastAPI, Depends 
from sqlmodel import SQLModel, Session
from app.order_db import engine
from app.crud import crud
from app.models.model import Order, OrderItem
from app.order_consumer import consume_messages
from contextlib import asynccontextmanager
import asyncio


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()
    task = asyncio.create_task(consume_messages())
    yield
    task.cancel()

app = FastAPI(
   lifespan=lifespan,
    description="AI Online Mart",
    title="Welcome to Product Service",
    version="0.0.1",
)

def get_db():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return{"message":"This is order service"}   

@app.post("/create-order", response_model=Order)
def create_order(order: Order, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.get("/get-order/{order_id}", response_model=OrderItem)
def read_order(order_id: int, db: Session = Depends(get_db)):
    return crud.read_order(db=db, order_id=order_id)

@app.put("/order_update/{order_id}", response_model=Order)
def update_order(order_id: int, db: Session = Depends(get_db)):
    return crud.update_order(db=db, order_id=order_id, order=Order)

@app.delete("/delete-order/{order_id}", response_model=Order)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return crud.delete_order(db=db, order_id=order_id)
