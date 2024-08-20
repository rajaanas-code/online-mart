from fastapi import FastAPI
from app.payment_consumer import consume_payment_messages
import asyncio


app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Payment Service",
    description="AI Online Mart",
    version="0.0.1",
)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_payment_messages("KAFKA_PAYMENT_TOPIC", "broker:19092"))

@app.get("/")
async def root():
    return {"message": "Payment Service"}
