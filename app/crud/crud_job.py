# app/crud/crud_job.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from datetime import datetime
from typing import Optional

from app.models.job import JobPost
from app.schemas.job import JobPostCreate, JobPostUpdate, JobSearch # Added JobSearch

def get_job(db: Session, job_id: uuid.UUID) -> JobPost | None:
    return db.query(JobPost).filter(JobPost.id == job_id).first()

def get_jobs(db: Session, skip: int = 0, limit: int = 100, search_params: Optional[JobSearch] = None) -> list[JobPost]:
    query = db.query(JobPost)

    if search_params:
        if search_params.RoleName:
            query = query.filter(JobPost.RoleName.ilike(f"%{search_params.RoleName}%"))
        if search_params.CompanyName:
            query = query.filter(JobPost.CompanyName.ilike(f"%{search_params.CompanyName}%"))
        if search_params.Location:
            query = query.filter(JobPost.Location.ilike(f"%{search_params.Location}%"))
        if search_params.DepartmentName:
            query = query.filter(JobPost.DepartmentName.ilike(f"%{search_params.DepartmentName}%"))
            
    return query.order_by(desc(JobPost.PostingDate)).offset(skip).limit(limit).all()

def create_job(db: Session, job: JobPostCreate) -> JobPost:
    job_data = job.model_dump()
    # Convert HttpUrl to string if it's the ApplicationLink
    if 'ApplicationLink' in job_data and job_data['ApplicationLink'] is not None:
        job_data['ApplicationLink'] = str(job_data['ApplicationLink'])

    db_job = JobPost(
        **job_data,
        PostingDate=datetime.utcnow() # Server sets the posting date
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, db_job: JobPost, job_in: JobPostUpdate) -> JobPost:
    job_data = job_in.model_dump(exclude_unset=True)

    # Convert HttpUrl to string for ApplicationLink if present
    if 'ApplicationLink' in job_data and job_data['ApplicationLink'] is not None:
        job_data['ApplicationLink'] = str(job_data['ApplicationLink'])

    for key, value in job_data.items():
        setattr(db_job, key, value)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: uuid.UUID) -> JobPost | None:
    db_job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job

def get_distinct_job_attributes(db: Session, column_name: str) -> list[str]:
    """Fetches distinct non-null and non-empty values for a given column in JobPost."""
    # Ensure the column_name is a valid attribute of JobPost to prevent SQL injection like issues
    if not hasattr(JobPost, column_name):
        raise ValueError(f"Invalid column name: {column_name}")
    
    query_result = db.query(getattr(JobPost, column_name)).distinct().all()
    # Filter out None or empty strings and convert to list of strings
    return [value for value, in query_result if value and str(value).strip()]
