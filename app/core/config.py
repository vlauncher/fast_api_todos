import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel

env_file = ".env.dev" if os.getenv("APP_ENV") == "development" else ".env.prod"
load_dotenv(dotenv_path=Path(env_file))

class Settings(BaseModel):
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # Email settings
    EMAIL_BACKEND: str = os.getenv("EMAIL_BACKEND")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST")
    EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
    EMAIL_USE_SSL: bool = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT"))
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")

settings = Settings()
