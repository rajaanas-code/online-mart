from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.product_model import ProductService

def add_new_product(product_data: ProductService, session: Session) -> ProductService:
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data

def get_all_products(session: Session):
    return session.exec(select(ProductService)).all()

def get_product_by_id(product_id: int, session: Session) -> ProductService:
    product = session.exec(select(ProductService).where(ProductService.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product