from sqlmodel import Session, select
from app.model.payment_model import Payment

def add_payment(payment_data: Payment, session: Session):
    session.add(payment_data)
    session.commit()
    session.refresh(payment_data)
    return payment_data

def get_payment_by_order(order_id: int, session: Session):
    return session.exec(select(Payment).where(Payment.order_id == order_id)).one_or_none()