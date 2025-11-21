from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import Session, select
from typing import List
from ..db import engine
from ..models import Habit, User
from ..auth_utils import create_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from ..auth_utils import SECRET_KEY, ALGORITHM
from fastapi import Body
from ..schemas import HabitCreate
from datetime import datetime



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


router = APIRouter(prefix="/habits", tags=["habits"])


# utility to get current user
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    with Session(engine) as session:
        user = session.get(User, uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


@router.get("/", response_model=List[Habit])
def list_habits(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(Habit).where(Habit.owner_id == current_user.id)
        return session.exec(statement).all()


@router.post("/", response_model=Habit)
def create_habit(habit_in: HabitCreate, current_user: User = Depends(get_current_user)):
    habit = Habit(
        name=habit_in.name,
        status=habit_in.status,
        owner_id=current_user.id,
        category=habit_in.category,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    with Session(engine) as session:
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


@router.put("/{habit_id}", response_model=Habit)
def update_habit(habit_id: int, habit_in: HabitCreate, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        habit = session.get(Habit, habit_id)
        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")
        if habit.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        habit.name = habit_in.name
        habit.status = habit_in.status
        habit.category = habit_in.category
        updated_at=datetime.utcnow()
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int = Path(..., ge=1), current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    if habit.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session.delete(habit)
    session.commit()
    return

@router.patch("/{habit_id}", response_model=Habit)
def patch_habit_status(
    habit_id: int,
    status: str = Body(..., embed=True),  # expects JSON {"status": "completed"}
    current_user: User = Depends(get_current_user),
):
    """
    Partially update only the 'status' field of a habit.
    Request body should be: {"status": "new-status"}
    """
    with Session(engine) as session:
        habit = session.get(Habit, habit_id)
        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")
        if habit.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        habit.status = status
        session.add(habit)
        habit.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(habit)
        return habit