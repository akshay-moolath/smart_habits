from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
class HabitCreate(BaseModel):
    name: str
    status: Optional[str] = "active"
    category: Optional[str] = None