# app/core/security.py
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext # For password hashing if needed later, not for OTP

from app.core.config import settings
from app.schemas.user import TokenPayload # Assuming TokenPayload is in user schemas

# If you were to hash passwords (not for OTP, but for traditional auth)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception: Exception) -> TokenPayload | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_sub = payload.get("sub")
        token_exp = payload.get("exp")
        
        if token_sub is None or token_exp is None:
            raise credentials_exception
        
        # Check if token is expired
        if datetime.fromtimestamp(token_exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise credentials_exception # Or a specific exception for expired token
            
        return TokenPayload(**payload) # Validate payload structure
    except JWTError:
        raise credentials_exception
    except Exception as e: # Catch any other validation errors from TokenPayload
        # print(f"Token payload validation error: {e}") # For debugging
        raise credentials_exception

def generate_otp(length: int = settings.OTP_LENGTH) -> str:
    """Generate a numeric OTP of a specified length."""
    if not isinstance(length, int) or length <= 0:
        raise ValueError("OTP length must be a positive integer.")
    # digits = string.digits
    # return "".join(secrets.choice(digits) for _ in range(length))
    # A more secure way to ensure it's exactly `length` digits and handles potential leading zeros if stored as int elsewhere
    # For string OTPs, the above is fine. If it needs to be an integer, be careful with leading zeros.
    # This ensures it's a string of digits.
    return "".join(secrets.choice(string.digits) for i in range(length))

# Example of password hashing (not used for OTP but good to have if you add password auth later)
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)
