# app/api/v1/endpoints/jobs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app import crud, schemas, models # Updated imports
from app.database import get_db # Updated import

router = APIRouter()

@router.post("/", response_model=schemas.JobPostInDB, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    job_in: schemas.JobPostCreate,
    db: Session = Depends(get_db)
):
    """
    Create new job posting.
    """
    return crud.create_job(db=db, job=job_in)

@router.get("/", response_model=List[schemas.JobPostInDB])
def read_job_postings(
    skip: int = 0,
    limit: int = 100,
    RoleName: Optional[str] = None, # Added search parameters
    CompanyName: Optional[str] = None,
    Location: Optional[str] = None,
    DepartmentName: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all job postings, with pagination and search filters.
    """
    search_params = schemas.JobSearch(
        RoleName=RoleName,
        CompanyName=CompanyName,
        Location=Location,
        DepartmentName=DepartmentName
    )
    jobs = crud.get_jobs(db, skip=skip, limit=limit, search_params=search_params)
    return jobs

@router.get("/{job_id}", response_model=schemas.JobPostInDB)
def read_job_posting(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific job posting by ID.
    """
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return db_job

@router.put("/{job_id}", response_model=schemas.JobPostInDB)
def update_single_job_posting(
    job_id: uuid.UUID,
    job_in: schemas.JobPostUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific job posting.
    """
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    updated_job = crud.update_job(db=db, db_job=db_job, job_in=job_in)
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_job_posting(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a specific job posting.
    """
    db_job = crud.delete_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return

@router.get("/suggestions/role-names", response_model=schemas.SuggestionList)
async def get_role_name_suggestions(db: Session = Depends(get_db)):
    """
    Get distinct role names for search suggestions.
    """
    suggestions = crud.get_distinct_job_attributes(db, "RoleName")
    return schemas.SuggestionList(suggestions=suggestions)

@router.get("/suggestions/company-names", response_model=schemas.SuggestionList)
async def get_company_name_suggestions(db: Session = Depends(get_db)):
    """
    Get distinct company names for search suggestions.
    """
    suggestions = crud.get_distinct_job_attributes(db, "CompanyName")
    return schemas.SuggestionList(suggestions=suggestions)

@router.get("/suggestions/locations", response_model=schemas.SuggestionList)
async def get_location_suggestions(db: Session = Depends(get_db)):
    """
    Get distinct locations for search suggestions.
    """
    suggestions = crud.get_distinct_job_attributes(db, "Location")
    return schemas.SuggestionList(suggestions=suggestions)

@router.get("/suggestions/department-names", response_model=schemas.SuggestionList)
async def get_department_name_suggestions(db: Session = Depends(get_db)):
    """
    Get distinct department names for search suggestions.
    """
    suggestions = crud.get_distinct_job_attributes(db, "DepartmentName")
    return schemas.SuggestionList(suggestions=suggestions)
