# app/crud/crud_user.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta, timezone
import uuid

from app.models.user import User, OTP
from app.schemas.user import UserCreate, UserUpdate, OTPRequest
from app.core.config import settings

# User CRUD operations
def get_user(db: Session, user_id: uuid.UUID) -> User | None:
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
        is_active=True, # Users are active by default upon creation
        is_admin=False # Users are not admins by default
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# OTP CRUD operations
def create_otp(db: Session, otp_code: str, identifier: str, expires_delta: timedelta, user_id: uuid.UUID | None = None) -> OTP:
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
