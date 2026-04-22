from fastapi import Security
from fastapi.security import APIKeyHeader

from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from X-API-Key header"""
    if api_key != settings.api.api_key:
        raise ValueError("Invalid API Key")
