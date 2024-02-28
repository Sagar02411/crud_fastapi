from sqlalchemy.orm import Session
from passlib.context import CryptContext
import model
import schema
from typing import List
import auth
from fastapi import HTTPException, Depends, status, Query


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_product_by_product_id(db: Session, product_id: int):
    return db.query(model.Products).filter(model.Products.id == product_id).first()


def get_product_by_name(db: Session, name: str):
    return db.query(model.Products).filter(model.Products.product_name == name).first()


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Products).offset(skip).limit(limit).all()


def add_product_details_to_db(db: Session, product: schema.ProductAdd):
    mv_details = model.Products(
        product_name=product.product_name,
        price=product.price,
        description=product.description
    )
    db.add(mv_details)
    db.commit()
    db.refresh(mv_details)
    return model.Products(**product.dict())


def update_product_details(db: Session, name: str, details: schema.UpdateProduct):
    print(details)
    db.query(model.Products).filter(model.Products.product_name == name).update(vars(details))
    db.commit()
    return db.query(model.Products).filter(model.Products.product_name == name).first()


def delete_product_details_by_name(db: Session, name: str):
    try:
        db.query(model.Products).filter(model.Products.product_name == name).delete()
        db.commit()
    except Exception as e:
        raise Exception(e)


def add_customer_details_to_db(first_name: str, last_name: str, address: str, phone_number: int, email: str, password: str, db: Session):
    password_hash = pwd_context.hash(password)
    mv_customer_details = model.Customers(
        first_name=first_name,
        last_name=last_name,
        address=address,
        phone_number=phone_number,
        email=email,
        password=password_hash
    )
    db.add(mv_customer_details)
    db.commit()
    db.refresh(mv_customer_details)
    return f"new user created as {first_name}"


def login_user(db: Session, request_email, request_password):
    user = db.query(model.Customers).filter(model.Customers.email == request_email).first()
    if not user:
        return {"message": "Invalid e-mail id"}
    is_match = pwd_context.verify(request_password, user.password)
    if not is_match:
        return {"message": "Invalid password!!"}
    return {"message:" "Login!!"}


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Customers.customer_id, model.Customers.first_name, model.Customers.last_name, model.Customers.address, model.Customers.email, model.Customers.phone_number).offset(skip).limit(limit).all()


def get_product_query(db: Session, name: str = Query(None), min_price: int = Query(None),max_price: int = Query(None), description: str = Query(None), add_by: str = Query(None)) -> List[schema.Product]:
    products = db.query(model.Products)

    if name:
        products = products.filter(model.Products.product_name.ilike(f"%{name}%"))

    if min_price:
        products = products.filter(model.Products.price >= min_price)

    if max_price:
        products = products.filter(model.Products.price <= max_price)

    if description:
        products = products.filter(model.Products.product_name.ilike(f"%{description}%"))

    if add_by:
        products = products.filter(model.Products.add_by == add_by)

    return products.all()