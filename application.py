from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, status, Query, UploadFile
from fastapi import Response
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from uuid import uuid4
from uuid import UUID
import boto3
import magic
from loguru import logger



import auth
import crud
import model
import schema
from db_handler import SessionLocal, engine

model.Base.metadata.create_all(bind=engine)


# KB = 1024
# MB = 1024 * KB
#
# SUPPORTED_FILE_TYPES = {
#     'image/png': 'png',
#     'image/jpeg': 'jpg',
# }


# session = boto3.Session(
#     aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
#     aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
# )


app = FastAPI(
    title="Products Details",
    description="You can perform CRUD operation by using this API",
    version="1.0.0"
)

# s3_client = boto3.client('s3')
#
# AWS_BUCKET = 'ecommerceimagesinnovatics'
#
# s3 = boto3.resource('s3')
# bucket = s3.Bucket(AWS_BUCKET)


# async def s3_upload(contents: bytes, key: str):
#     logger.info(f'Uploading {key} to s3')
#     bucket.put_object(Key=key, Body=contents)



origins = [
    "http://localhost:3000",
]

cookie_params = CookieParameters()

cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post('/upload')
# async def upload(file: UploadFile | None = None):
#     if not file:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='No file found!!'
#         )
#
#     contents = await file.read()
#     size = len(contents)
#
#     if not 0 < size <= 1 * MB:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='Supported file size is 0 - 1 MB'
#         )
#
#     file_type = magic.from_buffer(buffer=contents, mime=True)
#     if file_type not in SUPPORTED_FILE_TYPES:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f'Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES}'
#         )
#     file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[file_type]}'
#     await s3_upload(contents=contents, key=file_name)
#     return {'file_name': file_name}


@app.get('/product', response_model=List[schema.Product])
def retrieve_all_products_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db=db, skip=skip, limit=limit)
    return products


@app.post('/product', dependencies=[Depends(cookie)])
def add_new_product(product_name: str, price: int, description: str, image_url:str, session_data: schema.SessionData = Depends(auth.verifier), db: Session = Depends(get_db)):
    if not session_data.logged_in:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You need to be logged in to access products",
        )
    elif not product_name or not price or not description:
        raise HTTPException(status_code=404, detail=f"missing values")
    elif price < 0:
        raise HTTPException(status_code=404, detail=f"price can not less than zero!!!")
    mv_details = model.Products(
        product_name=product_name,
        price=price,
        description=description,
        add_by=session_data.username,
        image_URL=image_url
    )
    db.add(mv_details)
    db.commit()
    db.refresh(mv_details)
    return f"{product_name} added by {session_data.username}"


@app.delete('/product')
def delete_product_by_name(name: str, db: Session = Depends(get_db)):
    details = crud.get_product_by_name(db=db, name=name)
    if not details:
        raise HTTPException(status_code=404, detail=f"No record found to delete")

    try:
        crud.delete_product_details_by_name(db=db, name=name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to delete: {e}")
    return {"delete status": "success"}


@app.put('/product', response_model=schema.Product)
def update_product_details(name: str, update_param: schema.UpdateProduct, db: Session = Depends(get_db)):
    details = crud.get_product_by_name(db=db, name=name)
    if not details:
        raise HTTPException(status_code=404, detail=f"No record found to update")
    return crud.update_product_details(db=db, details=update_param, name=name)


@app.post('/signUp')
def add_new_customer(first_name: str, last_name: str, address: str, phone_number: int, email: str, password: str, db: Session = Depends(get_db)):
    return crud.add_customer_details_to_db(first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, email=email, password=password,db=db)


@app.post("/login")
async def login(response: Response, request_email: str, request_password: str, db: Session = Depends(get_db)):
    user = db.query(model.Customers).filter(model.Customers.email == request_email).first()
    if not user:
        return {"message": "Invalid e-mail id"}
    is_match = crud.pwd_context.verify(request_password, user.password)
    if not is_match:
        return {"message": "Invalid password!!"}

    session = uuid4()
    data = schema.SessionData(username=request_email, logged_in=True)

    await auth.backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"Logged in as {request_email}"


@app.get('/users', response_model=List[schema.Customer])
def retrieve_all_users_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/products")
def get_products_by_query(db: Session = Depends(get_db), name: str = Query(None), min_price: int = Query(None),
                          max_price: int = Query(None), description: str = Query(None), add_by: str = Query(None)):
    return crud.get_product_query(db, name, min_price, max_price, description, add_by)


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: schema.SessionData = Depends(auth.verifier)):
    return session_data


@app.post("/logout")
async def logout(response: Response, session_id: UUID = Depends(cookie)):
    session_data = await auth.backend.read(session_id)
    session_data.logged_in = False
    await auth.backend.update(session_id, session_data)
    cookie.delete_from_response(response)
    return "Logged out"

