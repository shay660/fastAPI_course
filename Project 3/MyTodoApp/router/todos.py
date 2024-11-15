from fastapi import Depends, Path, HTTPException, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated

from .auth import get_current_user
from ..models import ToDos
from ..database import LocalSession

router = APIRouter()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class ToDoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    return db.query(ToDos).filter(ToDos.user_id == user.get("user_id")).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    todo_model = db.query(ToDos).filter(ToDos.user_id == user.get("user_id")).filter(
        ToDos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: ToDoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed.")
    new_todo = ToDos(**todo_request.model_dump(), user_id=user.get('user_id'))
    db.add(new_todo)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: ToDoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    todo_model = db.query(ToDos).filter(ToDos.user_id == user.get("user_id")).filter(
        ToDos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(401, "Authentication Failed.")
    todo_model = db.query(ToDos).filter(ToDos.user_id == user.get('user_id')).filter(
        ToDos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    db.query(ToDos).filter(ToDos.user_id == user.get('user_id')).filter(
        ToDos.id == todo_id).delete()
    db.commit()
