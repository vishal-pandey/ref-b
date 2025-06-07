# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Union
import uuid
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$") # Basic E.164 pattern

# Properties to receive via API on creation
class UserCreate(UserBase):
    # Either email or mobile must be provided
    @model_validator(mode='before')
    @classmethod
    def check_email_or_mobile(cls, values):
        if not values.get('email') and not values.get('mobile_number'):
            raise ValueError('Either email or mobile number must be provided')
        return values

# Properties to receive via API on update
class UserUpdate(UserBase):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    is_active: bool
    is_admin: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Schemas for OTP
class OTPRequest(BaseModel):
    # User can request OTP via email or mobile
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")

    @model_validator(mode='before')
    @classmethod
    def check_email_or_mobile(cls, values):
        if bool(values.get('email')) == bool(values.get('mobile_number')):
             raise ValueError('Either email or mobile number must be provided, but not both.')
        return values

class OTPVerify(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    otp_code: str = Field(..., min_length=6, max_length=6) # Assuming OTP_LENGTH is 6

    @model_validator(mode='before')
    @classmethod
    def check_email_or_mobile(cls, values):
        if bool(values.get('email')) == bool(values.get('mobile_number')):
             raise ValueError('Either email or mobile number must be provided, but not both.')
        return values

# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Union[uuid.UUID, str] # Subject of the token (user_id)
    exp: Optional[datetime] = None

class Msg(BaseModel):
    msg: str
