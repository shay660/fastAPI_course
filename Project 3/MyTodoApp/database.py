from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

###### with sqlite ######
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Timmy1311@localhost/TodoApplicationDB"

engine = create_engine(url=SQLALCHEMY_DATABASE_URL)
# add this for sqlite: connect_args={"check_same_thread": False}

LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
