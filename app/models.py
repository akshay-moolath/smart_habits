from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import BaseModel



class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    hashed_password: str


class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    status: str = "active"
    owner_id: Optional[int] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HabitCreate(BaseModel):
    name: str
    status: Optional[str] = "active"
    category: Optional[str] = None


from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class MoodEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    habit_id: Optional[int] = Field(default=None, foreign_key="habit.id")  # <-- new foreign key
    text: str
    sentiment: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

