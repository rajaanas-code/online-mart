from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.product_model import ProductService

def add_new_product(product_data: ProductService, session: Session):
    print("Adding product to Database")
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data

def get_all_products(session: Session):
    all_product = session.exec(select(ProductService)).all()
    return all_product

def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(ProductService).where(ProductService.id == product_id)).one_or_none()
    if product is None:
        return HTTPException(status_code=404, detail="Product not found")
    return product

def update_product_item(product_id: int, product_data: ProductService, session: Session):
    product = session.exec(select(ProductService).where(ProductService.id == product_id)).first()
    if product:
        for key, value in product_data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        session.commit()
        session.refresh(product)
        return product
    raise HTTPException(status_code=404, detail=f"Item {product_id} is not found")

def delete_product_by_id(product_id: int, session: Session):
    product = session.exec(select(ProductService).where(ProductService.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"message" : "Product Deleted Successfully!"}



