from fastapi import FastAPI
from starlette import status

from .models import Base
from .database import engine
from .router import auth, todos, admin, users

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK)
async def check_healthy():
    return {"status": "Healthy"}


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
