from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session
from app.crud.payment_crud import add_payment
from app.payment_db import engine
from contextlib import asynccontextmanager
from app.payment_producer import get_kafka_producer, get_session
from app.models.payment_model import PaymentService
from app.utils.payment_email import send_email
from app.settings import STRIPE_API_KEY
import json
import stripe

# Set your Stripe secret key (test mode)
stripe.api_key = STRIPE_API_KEY

MY_DOMAIN = "http://localhost:8001"

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Payment Service with Stripe Integration",
    description="Online Mart API",
    version="0.0.2",
)

@app.post("/create-stripe-payment/")
async def create_stripe_payment(payment: PaymentService, session: Session = Depends(get_session)):
    """
    Creates a payment record and generates a Stripe checkout URL.
    """
    try:
        # Step 1: Add the payment to the database
        new_payment = add_payment(payment, session)

        # Step 2: Create Stripe Checkout Session
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Order Payment'},
                    'unit_amount': int(payment.amount * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{MY_DOMAIN}/stripe-callback/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{MY_DOMAIN}/payment-cancel",
        )

        # Step 3: Return payment details and the Stripe checkout URL
        return {
            "payment_details": {
                "id": new_payment.id,
                "order_id": new_payment.order_id,
                "amount": new_payment.amount,
                "status": new_payment.status,
                "payment_gateway": new_payment.payment_gateway
            },
            "checkout_url": stripe_session.url  # Return the Stripe checkout URL
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/stripe-callback/payment-success")
async def payment_success(session_id: str):
    """
    This endpoint is called after successful payment.
    """
    try:
        # Retrieve session details
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            return {
                "message": "Payment succeeded",
                "order_id": session.client_reference_id
            }
        else:
            return {"message": "Payment not successful"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing payment: {str(e)}")


@app.get("/payment-cancel")
async def payment_cancel():
    """
    This endpoint is called if the user cancels the payment.
    """
    return {"message": "Payment canceled by user."}