from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..database import LocalSession
from ..models import ToDos
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependence = Annotated[Session, Depends(get_db)]
user_dependence = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependence, db: db_dependence):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed.")
    return db.query(ToDos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependence, db: db_dependence, todo_id: int):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed.")
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    db.query(ToDos).filter(ToDos.id == todo_id).delete()
    db.commit()







