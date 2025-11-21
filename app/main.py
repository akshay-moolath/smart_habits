from fastapi import FastAPI
from .db import init_db


app = FastAPI(title="Smart Habits")


# initialize DB
@app.on_event("startup")
def on_startup():
    init_db()


# include routers
from .routes import moods
from .routes import auth, habits
app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(moods.router)
