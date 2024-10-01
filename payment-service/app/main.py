from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import Session, SQLModel
from aiokafka import AIOKafkaProducer
from typing import AsyncGenerator
from typing import Annotated
import stripe
import json

from typing import Any,Annotated
from app.payment_db import engine
from app.settings import STRIPE_API_KEY
from app.payment_producer import get_kafka_producer, get_session
from app.models.payment_model import Payment, PaymentCreate, PaymentUpdate
from app.auth import get_current_user, get_login_for_access_token, admin_required
from app.crud.payment_crud import create_payment, get_payment, payment_status_update, get_payment_intent_status
 
stripe.api_key = STRIPE_API_KEY

GetCurrentUserDep = Annotated[ Any, Depends(get_current_user)]
LoginForAccessTokenDep = Annotated[dict, Depends(get_login_for_access_token)]


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan, 
    title="Welcome To Payment Service",
    description="Online Mart API",
    version="0.0.1",

    # servers=[
    #     {
    #         "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
    #         "description": "Development Server"
    #     }
    #     ]
        )
        
@app.get("/")
def read_root():

    return {"Payment": "Services"}


@app.post("/auth/login")
def login(token:LoginForAccessTokenDep):
    return token

@app.post("/payments/")
async def create_payment_endpoint(payment: PaymentCreate, session: Session = Depends(get_session), current_user: Any = Depends(get_current_user)):
    pay_data,checkout_url = create_payment(session=session, payment_data=payment, user_id=current_user['id'],username=current_user['username'],email=current_user['email'])
    if checkout_url:
        return {"Payment":pay_data,"checkout_url": checkout_url}
    return {"payment": pay_data}

@app.get("/payments/{payment_id}", response_model=Payment,dependencies=[Depends(get_current_user)])
def read_payment(payment_id: int, session: Session = Depends(get_session), current_user: Any = Depends(get_current_user)):
    return get_payment(session, payment_id, current_user["id"])

@app.patch("/payments/{payment_id}", response_model=Payment,dependencies=[Depends(admin_required)])
def update_payment(payment_id: int, payment_update: PaymentUpdate, session: Session = Depends(get_session),current_user: Any = Depends(get_current_user)):
    payment = get_payment(session, payment_id, current_user["id"])
    updated_payment = payment_status_update(session, payment_id, payment_update.status)
    return updated_payment


@app.get("/stripe-callback/payment-success/")
async def payment_success(session_id: str, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    try:
        payment_status, order_id = get_payment_intent_status(session_id)
        if payment_status == "succeeded":
            payment = payment_status_update(session, order_id=order_id, status="completed")
            if payment:
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
            payment = payment_status_update(session, order_id=order_id, status="failed")
            return {"message": "Payment not completed", "payment_status": payment_status, "order_id": payment.order_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

@app.get("/stripe-callback/payment-fail/")
async def payment_fail(session_id: str, session: Session = Depends(get_session)):
    try:
        payment_status, order_id = get_payment_intent_status(session_id)
        payment = payment_status_update(session, order_id=order_id, status="failed")
        return {"message": "Payment failed", "payment_status": payment_status, "order_id": payment.order_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")