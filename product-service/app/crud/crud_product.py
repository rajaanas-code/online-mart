from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.model_product import ProductService

def add_new_product(product_data: ProductService, Session: Session):
    print("Adding product to Database")
    Session.add(product_data)
    Session.commit()
    Session.refresh(product_data)
    return product_data

def get_all_products(session: Session):
    all_product = session.exec(select(ProductService)).all()
    return all_product

def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(ProductService).where(ProductService.id == product_id)).one_or_none()
    if product is None:
        return HTTPException(status_code=404, detail="Product not found")
    return product


def delete_product_by_id(product_id: int, session: Session):
    product = session.exec(select(ProductService).where(ProductService.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"message" : "Product Deleted Successfully!"}



