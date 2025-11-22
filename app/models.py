from typing import Optional
from sqlmodel import SQLModel, Field, Column, Integer, Index
from datetime import datetime
from pydantic import BaseModel




class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    hashed_password: str


class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_habit_id: Optional[int] = Field(default=None, sa_column=Column("owner_habit_id", Integer, nullable=True))
    owner_id: Optional[int] = None
    name: str
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("ux_habit_owner_habit_id", "owner_id", "owner_habit_id", unique=True),
    )

class HabitCreate(BaseModel):
    name: str
    status: Optional[str] = "active"
    category: Optional[str] = None




class MoodEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    habit_id: Optional[int] = Field(default=None, foreign_key="habit.id")  # <-- new foreign key
    text: str
    sentiment: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)




