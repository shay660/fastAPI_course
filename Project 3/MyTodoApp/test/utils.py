from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest

from ..main import app
from ..database import Base
from ..models import ToDos

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(url=SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestLocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestLocalSession()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "shay660test", 'user_id': 1, "role": "admin"}


client = TestClient(app)


@pytest.fixture
def test_todo():
    try:
        todo1 = ToDos(id=1, title='Learn to code!', description="I need a job.", priority=5,
                      complete=False, user_id=1)
        todo2 = ToDos(id=2, title='Go to the store.', description="Buy eggs.", priority=3,
                      complete=False, user_id=1)
        todo3 = ToDos(id=3, title='Cut the grass.', description="It is getting long.",
                      priority=2, complete=False, user_id=2)

        db = TestLocalSession()
        db.add(todo1)
        db.add(todo2)
        db.add(todo3)
        db.commit()
    finally:
        yield
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM todos;"))
            connection.commit()
