# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.user import User as UserSchema, UserProfileUpdate # Pydantic schema for user output
from app.api import deps
from app.crud import crud_user
from app.models.user import User as UserModel # SQLAlchemy model

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[UserModel, Depends(deps.get_current_active_user)]
):
    """
    Get current logged-in user's details.
    The user object (including email, is_admin, etc.) is provided by the
    `get_current_active_user` dependency after validating the token.
    """
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: UserProfileUpdate,
    current_user: Annotated[UserModel, Depends(deps.get_current_active_user)]
):
    """
    Update current logged-in user's profile (full_name and/or mobile_number).
    """
    try:
        updated_user = crud_user.update_user_profile(db=db, db_user=current_user, profile_in=profile_in)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered by another user.",
        )
    except ValueError as e: # Catch specific ValueError from crud_user for no fields
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    return updated_user
