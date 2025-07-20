from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 300
    stripe_secret_key: str
    stripe_webhook_secret: str
    gemini_api_key: str
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
