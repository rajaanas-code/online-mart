from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session
from app.crud.payment_crud import add_payment, update_payment_status
from app.payment_db import engine
from contextlib import asynccontextmanager
from app.payment_producer import get_kafka_producer, get_session
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.models.payment_model import PaymentService
from app.utils.payment_email import send_email
from app.settings import STRIPE_API_KEY
import json
import stripe
import logging
import bcrypt

logger = logging.getLogger(__name__)

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

# User login endpoint
@app.post("/user-login/")
async def user_login(username: str, password: str, session: Session = Depends(get_session)):
    """
    Authenticates the user with the provided username and password.
    """
    try:
        # Fetch the user from the database (assuming you have a User model)
        user = session.query(user).filter(user.username == username).first()

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Check if the provided password matches the hashed password
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return {"message": "Authentication successful", "user_id": user.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

@app.post("/create-stripe-payment/")
async def create_stripe_payment(
    payment: PaymentService, 
    session: Session = Depends(get_session),
    username: str = Depends(user_login)  # Ensure user is authenticated
):
    """
    Creates a payment record and generates a Stripe checkout URL.
    """
    try:
        # Add the payment to the database
        new_payment = add_payment(payment, session)

        # Create Stripe Checkout Session
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
            client_reference_id=str(payment.order_id)  # Set client_reference_id to order_id
        )

        # Return payment details and the Stripe checkout URL
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

@app.get("/stripe-callback/payment-success/")
async def payment_success(
    session_id: str,
    session: Session = Depends(get_session),
    producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    """
    This endpoint is called after successful payment.
    """
    try:
        # Retrieve Stripe session details
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Log retrieved session details
        logger.info(f"Retrieved session ID: {session_id}")
        logger.info(f"Stripe session details: {stripe_session}")

        # Extract and validate the order ID
        order_id_str = stripe_session.client_reference_id
        if order_id_str is None:
            logger.error(f"Client reference ID is None for session ID: {session_id}")
            raise HTTPException(status_code=400, detail="Invalid session: Client reference ID is missing.")

        try:
            order_id = int(order_id_str)  # Convert order_id to integer
        except ValueError:
            logger.error(f"Failed to convert order ID to integer: {order_id_str}")
            raise HTTPException(status_code=400, detail="Invalid order ID format.")

        logger.info(f"Extracted order ID: {order_id}")

        payment_status = stripe_session.payment_status

        # Update payment status in the database
        if payment_status == "succeeded":
            payment = update_payment_status(session, order_id=order_id, status="completed")
            logger.info(f"Updated payment status for order ID {order_id}: {payment}")
            
            # Send Kafka messages and notifications
            event = {
                "order_id": payment.order_id,
                "status": "Paid",
                "user_id": payment.user_id,
                "amount": payment.amount,
            }
            await producer.send_and_wait("payment_succeeded", json.dumps(event).encode('utf-8'))

            notification_message = {
                "user_id": payment.user_id,
                "username": payment.username,
                "email": payment.email,
                "title": "Payment Sent",
                "message": f"Amount {payment.amount}$ has been sent successfully by {payment.username}.",
                "recipient": payment.email,
                "status": "succeeded"
            }
            notification_json = json.dumps(notification_message).encode("utf-8")
            await producer.send_and_wait("notification-topic", notification_json)

            return {"message": "Payment succeeded", "order_id": payment.order_id}
        else:
            payment = update_payment_status(session, order_id=order_id, status="failed")
            return {"message": "Payment not completed", "payment_status": payment_status, "order_id": payment.order_id}
    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing payment: {e}")
