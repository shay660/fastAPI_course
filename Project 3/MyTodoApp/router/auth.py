from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from jose import jwt

from ..database import LocalSession
from ..models import Users

router = APIRouter(prefix="/auth", tags=['auth'])

# use for hashing and verify the password
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# for the jwt stuff
oath2_bearer = OAuth2PasswordBearer(
    tokenUrl='auth/token')  # use for decode the jwt token.
SECRET_KEY = "CxUmWvrzmkGn93FZaapcqQBIY4F4CkKH"
ALGORTHM = "HS256"


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    is_active: bool = True
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependence = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username, 'id': user_id, 'exp': expires, 'role': role}
    return jwt.encode(encode, algorithm=ALGORTHM, key=SECRET_KEY)


async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORTHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate "
                                                        "the user")
        return {"username": username, "id": user_id, 'role': role}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate the user")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependence, create_user_request: CreateUserRequest):
    create_user_model = Users(email=create_user_request.email,
                              username=create_user_request.username,
                              first_name=create_user_request.first_name,
                              last_name=create_user_request.last_name,
                              hashed_password=bcrypt_context.hash(
                                  create_user_request.password), is_active=True,
                              role=create_user_request.role,
                              phone_number=create_user_request.phone_number)
    db.add(create_user_model)
    db.commit()


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependence):
    user: Users = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate "
                                                    "the user")
    access_token = create_access_token(user.username, user.id, user.role,
                                       timedelta(minutes=20))
    return {"access_token": access_token, "token_type": "bearer"}

