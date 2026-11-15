from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies.auth import get_current_user, get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def current_account(user: User = Depends(get_current_user)):
    return user

@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    profile : UserUpdate, db: Session = Depends(get_db), user : User = Depends(get_current_user)
) -> User:
    changes = profile.model_dump(exclude_unset=True)
    if changes is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "No Field Provided for update"
        )
    if "name" in changes and changes["name"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Display name cannot be null"
        )
    for field, value in changes.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Display name is already in use"
        )
    db.refresh(user)
    return user

@router.delete("/me", response_model=UserResponse)
def delete_my_account(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise