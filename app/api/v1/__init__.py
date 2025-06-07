from fastapi import APIRouter
from app.api.v1.endpoints import jobs as jobs_router
from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import users as users_router  # Import the new users router

api_router = APIRouter()

api_router.include_router(jobs_router.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router.router, prefix="/users", tags=["users"])  # Include the users router