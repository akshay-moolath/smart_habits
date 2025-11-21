from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlmodel import Session, select
from fastapi import Query
from sqlalchemy import desc as sql_desc, asc as sql_asc
from typing import List, Optional
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

ALLOWED_SORT_FIELDS = {"id", "name", "status", "category","created_at", "updated_at"}
@router.get("/", response_model=List[Habit])
def list_habits(
    status: Optional[str] = Query(None, description="Filter by status, e.g. active/completed"),
    category: Optional[str] = Query(None, description="Filter by category, e.g. health/work"),
    search: Optional[str] = Query(None, description="Search in habit name"), 
    sort: Optional[str] = Query("created_at", description="Sort field (id,name,status,category,created_at,updated_at)"),
    order: Optional[str] = Query("desc", description="'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
):
    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Allowed: {sorted(ALLOWED_SORT_FIELDS)}")

    # Build base statement
    with Session(engine) as session:
        statement = select(Habit).where(Habit.owner_id == current_user.id)

        if status:
            statement = statement.where(Habit.status == status)
        if category:
            statement = statement.where(Habit.category == category)
        if search:
            statement = statement.where(Habit.name.ilike(f"%{search}%"))

        # Resolve column and order
        column = getattr(Habit, sort)
        if order and order.lower() == "asc":
            statement = statement.order_by(sql_asc(column))
        else:
            # default desc
            statement = statement.order_by(sql_desc(column))

        # Pagination
        offset = (page - 1) * limit
        statement = statement.offset(offset).limit(limit)

        results = session.exec(statement).all()
        return results


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