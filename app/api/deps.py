# app/api/deps.py
from typing import Generator, Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Added
from jose import JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.models.user import User
from app.schemas.user import TokenPayload # Removed User as UserSchema is not used
from app.database import SessionLocal

# Changed from OAuth2PasswordBearer to HTTPBearer
reusable_oauth2 = HTTPBearer(
    bearerFormat="JWT", # Optional: good for documentation
    scheme_name="Bearer",
    auto_error=True
)

# New dependency for the static bearer token
automation_bearer_token_scheme = HTTPBearer(
    bearerFormat="Static",
    scheme_name="Bearer",
    auto_error=False # We will handle the error manually to allow JWT to proceed if this fails
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
    auth_credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(reusable_oauth2)], # Made optional
    automation_token_credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(automation_bearer_token_scheme)] # Added automation token
) -> User: # Return type changed to User (SQLAlchemy model)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, # This header is important
    )

    # Try automation token first
    if settings.AUTOMATION_BEARER_TOKEN and automation_token_credentials and automation_token_credentials.credentials == settings.AUTOMATION_BEARER_TOKEN:
        # For automation, we might not have a real user in the DB or need a specific one.
        # This example assumes a default or mock user for automation tasks.
        # You might need to adjust this based on your automation needs.
        # Option 1: Fetch a predefined automation user from DB
        # user = crud_user.get_user_by_email(db, email=settings.AUTOMATION_USER_EMAIL) 
        # if not user: raise HTTPException(status_code=403, detail="Automation user not found")
        # return user

        # Option 2: Return a mock/dummy User object if no DB interaction is needed for the call
        # This is simpler if the endpoint only checks for auth presence and not user details.
        # Ensure this mock user has necessary attributes if get_current_active_user checks them.
        print("Authenticated via static automation token.")
        # Create a dummy user or fetch a specific automation user
        # This part needs to be adapted to your application's logic for an automation user
        # For now, let's assume there's an admin user with ID 1 for automation, or create a mock one.
        user = crud_user.get_user(db, user_id=1) # Example: Get user with ID 1
        if not user:
            # Fallback or error if the designated automation user doesn't exist
            # This is a placeholder. You'll need to decide how to handle this.
            # For example, create a mock user object if no DB user is appropriate:
            # class MockUser: is_active = True; is_admin = True; id = 0; email = "automation@example.com"
            # return MockUser()
            raise HTTPException(status_code=500, detail="Automation user misconfigured or not found")
        return user

    # If not an automation token, or if automation token is not set/provided, try JWT
    if not auth_credentials:
        # This will be caught if auto_error=True on reusable_oauth2, 
        # but if we made it optional and no token was provided, raise manually.
        raise credentials_exception

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
    return user # Return SQLAlchemy model instance

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)] # Type hint changed to User
) -> User: # Return type changed to User
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin(
    current_user: Annotated[User, Depends(get_current_active_user)] # Type hint changed to User
) -> User: # Return type changed to User
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
