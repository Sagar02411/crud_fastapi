from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    id: int
    product_name: str
    price: int
    description: str
    add_by: str
    image_URL: str


class ProductAdd(ProductBase):
    class Config:
        orm_mode = True


class Product(ProductAdd):

    class Config:
        orm_mode = True


class UpdateProduct(BaseModel):
    id: Optional[int]
    product_name: Optional[str]
    price: Optional[int]
    description: Optional[str]
    add_by: Optional[str]
    image_URL: Optional[str]


    class Config:
        orm_mode = True


class CustomerBase(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    address: str
    phone_number: int
    email: str
    password: Optional[str]


class CustomerAdd(CustomerBase):
    class Config:
        orm_mode = True


class Customer(CustomerAdd):
    class Config:
        orm_mode = True


class SessionData(BaseModel):
    username: str
    logged_in: bool = False
