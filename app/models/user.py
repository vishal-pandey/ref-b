# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID # Keep for JobPost if it uses it, or remove if not used anywhere
import uuid # Keep for JobPost if it uses it
from datetime import datetime, timezone # Ensure this import is present

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Changed to Integer
    email = Column(String, unique=True, index=True, nullable=True)
    mobile_number = Column(String, unique=True, index=True, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Changed to Integer
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Changed to Integer
    email = Column(String, index=True, nullable=True)
    mobile_number = Column(String, index=True, nullable=True)
    otp_code = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
