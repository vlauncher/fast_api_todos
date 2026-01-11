from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas import User, UserUpdate
from app.services import update_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=User, summary="Get current user")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=User, summary="Update current user")
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_user(db, current_user, user_update)
