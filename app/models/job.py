# app/models/job.py
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone # Import timezone

from app.database import Base # Ensure Base is imported from your database setup

class JobPost(Base):
    __tablename__ = "job_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    PostingDate = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True) # Made nullable, added timezone
    RoleName = Column(String, index=True, nullable=True) # Added index
    DepartmentName = Column(String, nullable=True)
    Location = Column(String, index=True, nullable=True) # Added index
    CompanyName = Column(String, index=True, nullable=True) # Added index
    ContactEmail = Column(String, nullable=True)
    ApplicationLink = Column(String, nullable=True)
    JobDescription = Column(Text, nullable=True) # Made nullable
    ReferralStatus = Column(String, nullable=True) # Changed from Enum to String

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False) # Renamed to snake_case
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False) # Renamed to snake_case
