from pydantic_settings import BaseSettings

from src.core.config.base import BaseSettings


class APISettings(BaseSettings):
    api_key: str
