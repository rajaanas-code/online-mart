from sqlmodel import Session, select
from app.models.payment_model import PaymentService

def add_payment(payment_data: PaymentService, session: Session):
    session.add(payment_data)
    session.commit()
    session.refresh(payment_data)
    return payment_data

def get_payment_by_order(order_id: int, session: Session):
    return session.exec(select(PaymentService).where(PaymentService.order_id == order_id)).one_or_none()

def update_payment_status(session: Session, order_id: int, status: str) -> PaymentService:
    """
    Update the payment status for a given order ID.
    """
    payment = session.query(PaymentService).filter(PaymentService.order_id == order_id).first()

    if not payment:
        raise ValueError("Payment not found")

    payment.status = status
    session.commit()
    return payment