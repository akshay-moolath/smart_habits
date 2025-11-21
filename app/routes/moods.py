# app/routes/moods.py
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..db import engine
from ..models import MoodEntry, Habit, User
from ..schemas import MoodCreate, MoodRead
from ..nlp_utils import compute_sentiment_simple
from .habits import get_current_user

router = APIRouter(prefix="/moods", tags=["moods"])


@router.post("/", response_model=MoodRead, status_code=201)
def create_mood(mood_in: MoodCreate, current_user: User = Depends(get_current_user)):
    """
    Create a mood entry. Optionally attach it to a habit by providing `habit_id`.
    Validates that the habit exists and belongs to the current user.
    """
    # If a habit_id was provided, validate habit exists and belongs to current user
    if getattr(mood_in, "habit_id", None) is not None:
        with Session(engine) as session:
            habit = session.get(Habit, mood_in.habit_id)
            if not habit:
                raise HTTPException(status_code=404, detail="Habit not found")
            if habit.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to attach mood to this habit")

    sentiment_score = compute_sentiment_simple(mood_in.text)
    mood = MoodEntry(
        user_id=current_user.id,
        habit_id=getattr(mood_in, "habit_id", None),
        text=mood_in.text,
        sentiment=sentiment_score,
        created_at=datetime.utcnow(),
    )

    with Session(engine) as session:
        session.add(mood)
        session.commit()
        session.refresh(mood)
        return mood


@router.get("/", response_model=List[MoodRead])
def list_moods(
    habit_id: Optional[int] = Query(None, description="Filter moods by habit id"),
    limit: int = Query(50, ge=1, le=500, description="Max number of items to return"),
    current_user: User = Depends(get_current_user),
):
    """
    List moods for the current user. Optionally filter by habit_id.
    Returns newest entries first.
    """
    with Session(engine) as session:
        statement = select(MoodEntry).where(MoodEntry.user_id == current_user.id)
        if habit_id is not None:
            statement = statement.where(MoodEntry.habit_id == habit_id)
        statement = statement.order_by(MoodEntry.created_at.desc()).limit(limit)
        results = session.exec(statement).all()
        return results
