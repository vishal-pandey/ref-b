# app/schemas/__init__.py
from .job import JobPostCreate, JobPostUpdate, JobPostInDB, JobPostBase, JobSearch, SuggestionList
from .user import User, UserCreate, UserUpdate, OTPRequest, OTPVerify, Token, TokenPayload, Msg
