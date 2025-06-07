from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud, schemas, models
from app.core import security
from app.database import SessionLocal, engine
from app.core.config import settings

# models.Base.metadata.create_all(bind=engine) # This should be handled by Alembic migrations

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/request-otp", response_model=schemas.Msg)
async def request_otp(
    *,
    db: Session = Depends(get_db),
    otp_request: schemas.OTPRequest
):
    """
    Request an OTP for passwordless login.
    It will create a user if one doesn't exist with the provided identifier.
    """
    email = otp_request.email
    mobile = otp_request.mobile_number
    
    identifier_to_use: str
    user_create_data = {}

    if email:
        identifier_to_use = email.lower()
        user_create_data["email"] = email
    elif mobile:
        identifier_to_use = mobile # mobile is already a string, ensure it's stored as is or normalized if needed
        user_create_data["mobile_number"] = mobile
    else:
        # This case should be prevented by Pydantic's model_validator in OTPRequest schema
        raise HTTPException(status_code=400, detail="Email or mobile number must be provided.")

    user = crud.get_user_by_identifier(db, identifier=identifier_to_use)
    if not user:
        user_in_schema = schemas.UserCreate(**user_create_data)
        user = crud.create_user(db=db, user_in=user_in_schema)

    # Generate OTP
    otp_code = security.generate_otp()
    otp_expires_delta = timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    
    # Store OTP
    crud.create_otp(db=db, user_id=user.id, otp_code=otp_code, expires_delta=otp_expires_delta, identifier=identifier_to_use)
    
    # In a real application, you would send the OTP via email/SMS here.
    print(f"Generated OTP for {identifier_to_use}: {otp_code}") # Log OTP for testing
    return {"msg": f"OTP sent to {identifier_to_use}. It is: {otp_code}"} # Remove OTP from response in production


@router.post("/verify-otp", response_model=schemas.Token)
async def verify_otp(
    *,
    db: Session = Depends(get_db),
    otp_verify: schemas.OTPVerify
):
    """
    Verify OTP and return a JWT token if successful.
    """
    email = otp_verify.email
    mobile = otp_verify.mobile_number
    identifier_to_use: str

    if email:
        identifier_to_use = email.lower()
    elif mobile:
        identifier_to_use = mobile
    else:
        # This case should be prevented by Pydantic's model_validator
        raise HTTPException(status_code=400, detail="Email or mobile number must be provided.")

    user = crud.get_user_by_identifier(db, identifier=identifier_to_use)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please request an OTP first.",
        )

    db_otp = crud.get_valid_otp(db=db, identifier=identifier_to_use, otp_code=otp_verify.otp_code)

    if not db_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP.",
        )

    # Mark OTP as used
    crud.mark_otp_as_used(db=db, db_otp=db_otp)

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires # Ensure subject is string for JWT
    )
    return {"access_token": access_token, "token_type": "bearer"}
