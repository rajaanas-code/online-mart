from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session
from app.crud.payment_crud import add_payment, get_payment_by_order
from app.payment_db import engine
from contextlib import asynccontextmanager
from app.payment_producer import get_kafka_producer, get_session
from app.models.payment_model import PaymentService
from app.utils.payment_email import send_email
from app.settings import STRIPE_API_KEY
import json
import stripe

# Set your Stripe secret key (test mode)
stripe.api_key = "sk_test_51Pwzr1Kt0JUMFNogQPOMEAKdavEHcDsLXIp7AzOCVIRqAZesf8BwlJDF1AjeH4Xtk8qWycHyCgAC9Loht4XJfpVj0064HFoaUp"

YOUR_DOMAIN = "http://localhost:8008"

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Payment Service with Stripe Integration",
    description="Online Mart API - Payments",
    version="0.0.2",
)

@app.post("/create-stripe-payment/")
async def create_stripe_payment(amount: int, session: Session = Depends(get_session)):
    """
    This endpoint creates a Stripe Checkout session and returns the payment URL.
    """
    try:
        # Create Stripe Checkout Session
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Payment for Order'},
                    'unit_amount': amount,  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"http://localhost:8001/stripe-callback/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"http://localhost:8002/payment-cancel",
        )

        return {"url": stripe_session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/payments/", response_model=PaymentService)
async def create_new_payment(payment: PaymentService, session: Session = Depends(get_session)):
    """
    Creates a new payment record and triggers Kafka and email notifications.
    """
    try:
        # Add payment to the database
        new_payment = add_payment(payment, session)

        # Send notification to Kafka
        producer = await get_kafka_producer()
        notification_data = {
            "type": "payment_processed",
            "message": f"Payment of {new_payment.amount} for order ID {new_payment.order_id} processed successfully."
        }
        await producer.send_and_wait("notification-events", json.dumps(notification_data).encode("utf-8"))
        
        # Send email notification
        send_email(
            recipient="rajaanasturk157@gmail.com",
            subject="Payment Confirmation",
            message=f"Your payment of ${new_payment.amount} for order ID {new_payment.order_id} has been completed successfully."
        )

        return new_payment

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payment processing failed: {str(e)}")


@app.get("/stripe-callback/payment-success")
async def payment_success(order_id: int):
    return {
        "message": "Payment succeeded",
        "order_id": order_id
    }


@app.get("/payment-cancel")
async def payment_cancel():
    return {"message": "Payment canceled by user."}


@app.get("/payments/order/{order_id}", response_model=PaymentService)
def read_payment(order_id: int, session: Session = Depends(get_session)):
    return get_payment_by_order(order_id, session)