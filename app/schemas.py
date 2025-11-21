from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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

class MoodCreate(BaseModel):
    text: str
    habit_id: Optional[int] = None   # <-- optional link to a habit

class MoodRead(BaseModel):
    id: int
    user_id: int
    habit_id: Optional[int] = None
    text: str
    sentiment: Optional[float] = None
    created_at: datetime