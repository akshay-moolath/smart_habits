# app/db.py
import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import URL

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./habits.db")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

def init_db():
    SQLModel.metadata.create_all(engine)
