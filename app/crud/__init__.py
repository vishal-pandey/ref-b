# app/crud/__init__.py
from .crud_job import (
    create_job,
    delete_job,
    get_distinct_job_attributes,
    get_job,
    get_jobs,
    update_job,
)
from .crud_user import (
    create_otp,
    create_user,
    get_user,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_mobile,
    mark_otp_as_used,
    update_user,
    get_valid_otp,
)
