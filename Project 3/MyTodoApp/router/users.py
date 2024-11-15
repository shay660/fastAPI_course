from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

from ..database import LocalSession
from ..models import Users
from .auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependence = Annotated[Session, Depends(get_db)]
user_dependence = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated=['auto'])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependence, db: db_dependence):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependence, db: db_dependence, new_password: str):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(401, "Authentication Failed.")
    user_model.hashed_password = bcrypt_context.hash(new_password)
    db.add(user_model)
    db.commit()


@router.put("/update_phone_number/phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(db: db_dependence, user: user_dependence, phone_number):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(401, "Authentication Failed.")
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()

