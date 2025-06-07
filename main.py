from fastapi import FastAPI

from app.api.v1 import api_router as api_v1_router # Import the v1 router
from app.database import engine #, Base # Import engine and Base
# from app.models import * # Ensure models are imported if not done elsewhere for Base

# Create database tables (Alembic is preferred for production)
# For initial table creation if not using Alembic immediately, or for dev:
# from app.models.job import JobPost # Ensure your models are imported before create_all
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="The Referral Network API - Structured")

app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "Welcome to The Referral Network API - Structured Version"}

# The Uvicorn run command should be executed from the terminal:
# uvicorn main:app --reload
