# app/models/__init__.py
from app.database import Base # Import Base
from .job import JobPost
from .user import User, OTP  # Add User and OTP models
