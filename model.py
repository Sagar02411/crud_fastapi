from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db_handler import Base
from datetime import datetime

class Products(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    product_name = Column(String(255), index=True, nullable=False)
    price = Column(Integer, index=True, nullable=False)
    description = Column(String(255), index=True, nullable=False)
    add_by = Column(String(255), index=True, nullable=False)
    image_URL = Column(String(255), index=True)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True)
    delete_at = Column(DateTime, index=True)


class Customers(Base):
    __tablename__ = "customer"
    customer_id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    first_name = Column(String(255), index=True, nullable=False)
    last_name = Column(String(255), index=True, nullable=False)
    address = Column(String(255), index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True)
    delete_at = Column(DateTime, index=True)

class Payment(Base):
    __tablename__ = "payment"
    payment_id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    payment_type = Column(String(255), index=True, nullable=False)
    is_successful = Column(Boolean, index=True, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True)
    delete_at = Column(DateTime, index=True)


class Order(Base):
    __tablename__ = "order"
    order_id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    order_date = Column(Date, index=True)
    Quantity = Column(Integer, primary_key=False, index=True, autoincrement=False, nullable=False)
    total_price = Column(Integer, primary_key=False, index=True, autoincrement=False, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True)
    delete_at = Column(DateTime, index=True)

    # Foreign Keys
    customer_id = Column(Integer, ForeignKey('customer.customer_id'), nullable=False)
    payment_id = Column(Integer, ForeignKey('payment.payment_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)

    # Relationships
    customer = relationship("Customers", backref="orders")
    payment = relationship("Payment", backref="orders")
    product = relationship("Products", backref="orders")




