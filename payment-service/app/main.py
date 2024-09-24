from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from requests import session
from sqlmodel import SQLModel, Session
from app.crud.payment_crud import add_payment, update_payment_status
from app.payment_db import engine
from contextlib import asynccontextmanager
from app.models.payment_model import PaymentService
import stripe
import logging
import httpx
from app.payment_producer import get_session

logger = logging.getLogger(__name__)

# Set your Stripe secret key (test mode)
stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'

MY_DOMAIN = "http://localhost:8008"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

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

@app.post("/auth")
async def login(username: str, email: str, password: str):
   """
   Authenticate user and return an access token.
   """
   user_service_url = "http://user-service:8006/login"  # Use HTTPS here if available
   
   async with httpx.AsyncClient() as client:
       response = await client.post(user_service_url, json={"username": username, "email": email, "password": password})
   
   if response.status_code == 200:
       return {"message": "Login successful", "user_id": response.json()["user_id"]}
   else:
       raise HTTPException(status_code=response.status_code, detail="Authentication failed")

@app.post("/create-stripe-payment/")
async def create_stripe_payment(
   payment: PaymentService,
   auth: str = Depends(oauth2_scheme),
   session: Session = Depends(get_session),
):
   """
   Creates a payment record and generates a Stripe checkout URL.
   """
   # Optionally verify the token here if needed
   
   # Proceed with payment processing 
   try:
       new_payment = add_payment(payment , session)

       # Create Stripe Checkout Session 
       stripe_session=stripe.checkout.Session.create( 
           payment_method_types=['card'], 
           line_items=[{ 'price_data':{ 'currency':'usd', 'product_data':{'name':'Order Payment'}, 'unit_amount':int(payment.amount *100), }, 'quantity':1 , }, ], 
           mode='payment', 
           success_url=f"{MY_DOMAIN}/stripe-callback/payment-success?session_id={{CHECKOUT_SESSION_ID}}", 
           cancel_url=f"{MY_DOMAIN}/payment-cancel", 
           client_reference_id=str(payment.order_id)  # Set client_reference_id to order_id 
       )

       return { 
           "payment_details":{ 
               "id":new_payment.id , 
               "order_id":new_payment.order_id , 
               "amount":new_payment.amount , 
               "status":new_payment.status , 
               "payment_gateway":new_payment.payment_gateway 
           }, 
           "checkout_url":stripe_session.url  # Return the Stripe checkout URL 
       }

   except Exception as e:
       raise HTTPException(status_code=400 , detail=str(e))

@app.get("/stripe-callback/payment-success/")
async def payment_success(session_id:str):
   """
   This endpoint is called after successful payment.
   """
   try:
       # Retrieve Stripe session details 
       stripe_session=stripe.checkout.Session.retrieve(session_id) 

       # Extract and validate the order ID 
       order_id_str=stripe_session.client_reference_id 
       if order_id_str is None:
           logger.error(f"Client reference ID is None for session ID: {session_id}") 
           raise HTTPException(status_code=400 , detail="Invalid session: Client reference ID is missing.")

       try:
           order_id=int(order_id_str)  # Convert order_id to integer 
       except ValueError:
           logger.error(f"Failed to convert order ID to integer: {order_id_str}") 
           raise HTTPException(status_code=400 , detail="Invalid order ID format.")

       logger.info(f"Extracted order ID: {order_id}")

       payment_status=stripe_session.payment_status

       # Update payment status in the database 
       if payment_status=="succeeded":
           payment=update_payment_status(session , order_id=order_id , status="completed") 
           logger.info(f"Updated payment status for order ID {order_id}: {payment}") 

           return {"message":"Payment succeeded" ,"order_id":payment.order_id}
       else:
           payment=update_payment_status(session , order_id=order_id , status="failed") 
           return {"message":"Payment not completed" ,"payment_status":payment_status ,"order_id":payment.order_id}
   
   except Exception as e:
       logger.error(f"Error processing payment: {e}") 
       raise HTTPException(status_code=500 , detail=f"Error processing payment: {e}")