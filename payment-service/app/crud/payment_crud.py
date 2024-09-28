from app.models.payment_model import Payment, PaymentCreate, PaymentUpdate
from app.settings import STRIPE_API_KEY
from sqlmodel import Session, select
from fastapi import HTTPException
import stripe

stripe.api_key = STRIPE_API_KEY

def create_payment(session: Session, payment_data: PaymentCreate, user_id: int,username:str,email:str):
    if payment_data.method == "stripe":
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Order {}'.format(payment_data.order_id),
                    },
                    'unit_amount': int(payment_data.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
           success_url="http://localhost:8001/stripe-callback/payment-success/?session_id={CHECKOUT_SESSION_ID}",
           cancel_url="http://localhost:8002/stripe-callback/payment-fail/?session_id={CHECKOUT_SESSION_ID}",
            metadata={'order_id': payment_data.order_id, 'user_id': user_id}
        )
        payment = Payment(
            order_id=payment_data.order_id,
            user_id=user_id,
            username=username,
            email=email,
            amount=payment_data.amount,
            currency="usd",
            status="pending",
            method="stripe",
            stripe_payment_intent_id=checkout_session['id']
        )
    else:
        payment = Payment(
            order_id=payment_data.order_id,
            user_id=user_id,
            amount=payment_data.amount,
            username=username,
            email=email,
            currency="usd",
            status="pending",
            method="cash_on_delivery"
        )
    session.add(payment)
    session.commit()
    session.refresh(payment)    
    if payment_data.method == "stripe":
        return payment, checkout_session.url    
    return payment, None


def get_payment(session: Session, payment_id: int, user_id: int) -> Payment:
    payment = session.exec(select(Payment).where(Payment.id == payment_id, Payment.user_id == user_id)).one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

def payment_status_update(session: Session, order_id: int, status: str):
    payment = session.exec(select(Payment).where(Payment.order_id == order_id)).one_or_none()
    if payment:
        payment.status = status
        session.add(payment)
        session.commit()
        session.refresh(payment)
    else:
        raise HTTPException(status_code=404, detail=f"Payment not found for order_id: {order_id}")
    return payment

def get_payment_intent_status(session_id: str):
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    payment_intent = stripe.PaymentIntent.retrieve(checkout_session['payment_intent'])
    order_id = int(checkout_session['metadata']['order_id'])
    return payment_intent['status'], order_id