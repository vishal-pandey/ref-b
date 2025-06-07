# app/core/config.py
from pydantic_settings import BaseSettings
import secrets # For generating a default secret key

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://referral_user:referral_password@localhost:5432/referral_network"
    # API settings
    API_V1_STR: str = "/api/v1"

    # JWT settings
    SECRET_KEY: str = secrets.token_urlsafe(32) # Default to a securely generated key
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # OTP settings
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6


    class Config:
        env_file = ".env"
        # You can add more environment variables here and they will be loaded from .env
        # Example:
        # POSTGRES_USER: str
        # POSTGRES_PASSWORD: str
        # POSTGRES_DB: str
        # POSTGRES_HOST: str = "localhost"
        # POSTGRES_PORT: int = 5432
        # DATABASE_URL: Optional[str] = None

        # @validator("DATABASE_URL", pre=True)
        # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        #     if isinstance(v, str):
        #         return v
        #     return PostgresDsn.build(
        #         scheme="postgresql",
        #         user=values.get("POSTGRES_USER"),
        #         password=values.get("POSTGRES_PASSWORD"),
        #         host=values.get("POSTGRES_HOST"),
        #         port=str(values.get("POSTGRES_PORT")),
        #         path=f"/{values.get('POSTGRES_DB') or ''}",
        #     )

settings = Settings()
