from fastapi import APIRouter
from app.api.v1.endpoints import jobs as jobs_router
from app.api.v1.endpoints import auth as auth_router

api_router = APIRouter()

api_router.include_router(jobs_router.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])