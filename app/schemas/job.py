# app/schemas/job.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
import uuid

# Schema for creating a new job post (request)
class JobPostCreate(BaseModel):
    RoleName: str = Field(..., example="Senior Software Engineer")
    DepartmentName: Optional[str] = Field(None, example="Product Development")
    Location: Optional[str] = Field(None, example="Bengaluru, Karnataka")
    CompanyName: str = Field(..., example="Acme Corporation")
    ContactEmail: Optional[str] = Field(None, example="careers@acme.com") # Pydantic's EmailStr can also be used for validation
    ApplicationLink: Optional[HttpUrl] = Field(None, example="https://jobs.acme.com/apply/123")
    JobDescription: str = Field(..., example="We are looking for a motivated...")
    ReferralStatus: Optional[str] = Field(None, example="yes") # Changed from Literal to Optional[str]

# Schema for updating an existing job post (request)
class JobPostUpdate(BaseModel):
    RoleName: Optional[str] = None
    DepartmentName: Optional[str] = None
    Location: Optional[str] = None
    CompanyName: Optional[str] = None
    ContactEmail: Optional[str] = None
    ApplicationLink: Optional[HttpUrl] = None
    JobDescription: Optional[str] = None
    ReferralStatus: Optional[str] = None # Changed from Literal to Optional[str]

# Schema for representing a job post in responses (also used as base for JobPostInDB)
class JobPostBase(BaseModel):
    id: uuid.UUID
    PostingDate: datetime
    RoleName: str
    DepartmentName: Optional[str] = None
    Location: Optional[str] = None
    CompanyName: str
    ContactEmail: Optional[str] = None
    ApplicationLink: Optional[HttpUrl] = None
    JobDescription: str
    ReferralStatus: Optional[str] = None # Changed from Literal to Optional[str]

    class Config:
        from_attributes = True # Replaces orm_mode = True in Pydantic v2

# Schema for reading/returning a job post from the DB (response)
class JobPostInDB(JobPostBase):
    pass # Inherits all fields and config from JobPostBase

class JobSearch(BaseModel):
    RoleName: Optional[str] = None
    CompanyName: Optional[str] = None
    Location: Optional[str] = None
    DepartmentName: Optional[str] = None
    keyword: Optional[str] = Field(None, example="Python Developer") # Generic keyword search
    # Add any other fields you want to be searchable

class SuggestionList(BaseModel):
    suggestions: List[str]
