from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENWEATHER_API_KEY: str
    DATABASE_URL: str
    REDIS_URL: str
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
