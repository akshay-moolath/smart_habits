from fastapi import FastAPI
from .db import init_db
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .routes import moods
from .routes import auth, habits
from sqlmodel import SQLModel
from .db import engine


app = FastAPI(title="Smart Habits")


# initialize DB
@app.on_event("startup")
def on_startup():
    init_db()


# include routers

app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(moods.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join("static", "login.html"))

