from app.models.order_model import Order
from sqlmodel import Session, select
from fastapi import HTTPException
import requests

def send_order_to_kafka(session: Session, order: Order, product_price: float):
    order.total_price = order.quantity * product_price
    return order

def place_order(session: Session, order: Order):
    order.status = "Unpaid"  
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def get_order(session: Session, order_id: int) -> Order:
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found or not authorized")
    return order

def get_all_orders(session: Session) -> list[Order]:
    statement = select(Order)
    return session.exec(statement).all()

def update_order_status(session: Session, order_id: int, status: str):
    order = get_order(session, order_id)
    order.status = status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def delete_order(session: Session, order_id: int):
    order = get_order(session, order_id)
    session.delete(order)
    session.commit()
    return {"message": "Order deleted successfully"}

def get_product_price(product_id: int, token: str | None) -> float:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f'http://product-service:8007/products/{product_id}', headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch product price. Status code: {response.status_code}, Response: {response.text}")
    
    response_data = response.json()
    
    if 'price' not in response_data:
        raise HTTPException(status_code=404, detail="Product price not found")
    
    return response_data['price']