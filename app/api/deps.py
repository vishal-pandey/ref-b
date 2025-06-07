# app/api/deps.py
from typing import Generator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Added
from jose import JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.models.user import User
from app.schemas.user import TokenPayload, User as UserSchema # Added UserSchema
from app.database import SessionLocal

# Changed from OAuth2PasswordBearer to HTTPBearer
reusable_oauth2 = HTTPBearer(
    bearerFormat="JWT", # Optional: good for documentation
    scheme_name="Bearer",
    auto_error=True
)

# The tokenUrl was for OAuth2PasswordBearer documentation, 
# with HTTPBearer, the user gets the token from /auth/verify-otp 
# and then uses it.

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Annotated[Session, Depends(get_db)], 
    # token: Annotated[str, Depends(reusable_oauth2)] # Changed
    auth_credentials: Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)] # Changed
) -> UserSchema: # Return type changed to UserSchema
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, # This header is important
    )
    try:
        token = auth_credentials.credentials # Extract token from credentials
        payload = security.verify_token(token, credentials_exception)
        if payload.sub is None:
            raise credentials_exception
        
        # Ensure user_id is an integer
        try:
            user_id = int(payload.sub)
        except ValueError:
            # This case should ideally not happen if tokens are generated correctly
            # and sub is always a string representation of an int.
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    except Exception: # Catch potential validation errors from TokenPayload
        raise credentials_exception
        
    user = crud_user.get_user(db, user_id=user_id) # type: ignore
    if user is None:
        raise credentials_exception
    return UserSchema.model_validate(user) # Validate and return as UserSchema

async def get_current_active_user(
    current_user: Annotated[UserSchema, Depends(get_current_user)] # Type hint changed to UserSchema
) -> UserSchema: # Return type changed to UserSchema
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)] # Type hint changed to UserSchema
) -> UserSchema: # Return type changed to UserSchema
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
