from sqlmodel import Session, select
from fastapi import HTTPException
from app.model.order_model import Order

def create_order(order_data: Order, session: Session) -> Order:
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

def get_order_by_id(order_id: int, session: Session) -> Order:
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order