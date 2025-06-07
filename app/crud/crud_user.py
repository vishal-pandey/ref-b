# app/crud/crud_user.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, exc as sa_exc # Added sa_exc for handling unique constraint errors
from datetime import datetime, timedelta, timezone
# import uuid # uuid is not used for User/OTP IDs anymore

from app.models.user import User, OTP
from app.schemas.user import UserCreate, UserUpdate, OTPRequest, UserProfileUpdate # Added UserProfileUpdate
from app.core.config import settings

# User CRUD operations
def get_user(db: Session, user_id: int) -> User | None: # Changed user_id type to int
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_mobile(db: Session, mobile_number: str) -> User | None:
    return db.query(User).filter(User.mobile_number == mobile_number).first()

def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    """Gets a user by either email or mobile number."""
    return db.query(User).filter(or_(User.email == identifier, User.mobile_number == identifier)).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        mobile_number=user_in.mobile_number,
        full_name=user_in.full_name, # Added full_name
        is_active=True, 
        is_admin=False 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except sa_exc.IntegrityError: # Catch potential unique constraint violations (e.g., email/mobile)
        db.rollback()
        # Depending on which field caused it, you might want to raise a specific HTTPException
        # For now, re-raise to be handled by the endpoint or a generic error handler
        raise
    return db_user

def update_user_profile(db: Session, db_user: User, profile_in: UserProfileUpdate) -> User:
    """Updates a user's full_name and/or mobile_number."""
    updated = False
    if profile_in.full_name is not None:
        db_user.full_name = profile_in.full_name
        updated = True
    if profile_in.mobile_number is not None:
        # Check if the new mobile number is already taken by another user
        existing_user_with_mobile = get_user_by_mobile(db, mobile_number=profile_in.mobile_number)
        if existing_user_with_mobile and existing_user_with_mobile.id != db_user.id:
            # This specific error should be caught and handled in the endpoint
            # to return a proper HTTP 409 Conflict or similar.
            # For now, we can raise a ValueError or a custom exception.
            raise ValueError(f"Mobile number {profile_in.mobile_number} is already in use by another account.")
        db_user.mobile_number = profile_in.mobile_number
        updated = True
    
    if updated:
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        except sa_exc.IntegrityError: # Should be less likely here if checks are done above
            db.rollback()
            raise # Re-raise to be handled by endpoint
    return db_user

# OTP CRUD operations
def create_otp(db: Session, otp_code: str, identifier: str, expires_delta: timedelta, user_id: int | None = None) -> OTP: # Changed user_id type to int
    expires_at = datetime.now(timezone.utc) + expires_delta
    db_otp = OTP(
        user_id=user_id,
        email=identifier if "@" in identifier else None, # Basic check for email
        mobile_number=identifier if "@" not in identifier else None,
        otp_code=otp_code,
        expires_at=expires_at,
        used=False
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def get_valid_otp(db: Session, otp_code: str, identifier: str) -> OTP | None:
    """Retrieves an OTP if it exists, is not used, and has not expired."""
    now = datetime.now(timezone.utc)
    # Ensure user_id is also matched if available in OTP table, 
    # and identifier (email/mobile) is matched.
    # This is a more robust check.
    user = get_user_by_identifier(db, identifier=identifier)
    if not user:
        return None # Or raise an error, depending on desired behavior

    query = db.query(OTP).filter(
        OTP.user_id == user.id, # Match user_id
        OTP.otp_code == otp_code,
        OTP.used == False,
        OTP.expires_at > now
    )
    
    return query.first()

def mark_otp_as_used(db: Session, db_otp: OTP) -> OTP:
    db_otp.used = True
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp
