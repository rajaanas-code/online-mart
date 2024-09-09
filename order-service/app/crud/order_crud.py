from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.order_model import OrderService

def create_order(order_data: OrderService, session: Session) -> OrderService:
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

def get_order_by_id(order_id: int, session: Session) -> OrderService:
    order = session.exec(select(OrderService).where(OrderService.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order