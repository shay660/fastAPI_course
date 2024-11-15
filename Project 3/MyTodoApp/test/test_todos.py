from starlette import status

from ..router.todos import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": 1, "title": 'Learn to code!', "description": "I need a job.",
         "priority": 5, "complete": False, "user_id": 1},
        {"id": 2, "title": 'Go to the store.', "description": "Buy eggs.", "priority": 3,
         "complete": False, "user_id": 1},
]


def test_read_one_todo(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "title": 'Learn to code!',
                               "description": "I need a job.", "priority": 5,
                               "complete": False, "user_id": 1}


def test_read_todo_not_found(test_todo):
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}


def test_create_todo(test_todo):
    request_date = {"title": "New todo", "description": "New todo description.",
                    "priority": 3, "complete": False}
    response = client.post("/todo", json=request_date)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestLocalSession()
    response_data = db.query(ToDos).filter(ToDos.id == 4).first()
    assert response_data.title == request_date.get('title')
    assert response_data.description == request_date.get('description')
    assert response_data.priority == request_date.get('priority')
    assert response_data.complete == request_date.get('complete')


def test_update_todo(test_todo):
    request_date = {"title": "New todo title", "description": "I need a job.",
                    "priority": 5, "complete": False}
    response = client.put("/todo/1", json=request_date)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestLocalSession()
    response_data = db.query(ToDos).filter(ToDos.id == 1).first()
    assert response_data.title == request_date.get('title')
    assert response_data.description == request_date.get('description')
    assert response_data.priority == request_date.get('priority')
    assert response_data.complete == request_date.get('complete')


def test_update_todo_not_found(test_todo):
    request_date = {"title": "New todo title", "description": "I need a job.",
                    "priority": 5, "complete": False}
    response = client.put("/todo/999", json=request_date)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}


def test_delete_todo(test_todo):
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestLocalSession()
    todo_model = db.query(ToDos).filter(ToDos.id == 1).first()
    assert todo_model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}
