from .utils import *
from ..router.admin import get_db, get_current_user
from starlette import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": 1, "title": 'Learn to code!', "description": "I need a job.",
         "priority": 5, "complete": False, "user_id": 1},
        {"id": 2, "title": 'Go to the store.', "description": "Buy eggs.", "priority": 3,
         "complete": False, "user_id": 1},
        {"id": 3, "title": 'Cut the grass.', "description": "It is getting long.",
         "priority": 2, "complete": False, "user_id": 2}]


def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/3")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestLocalSession()
    model = db.query(ToDos).filter(ToDos.id == 3).first()
    assert model is None


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete('/admin/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}
