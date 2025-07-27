# verify_project/app/security/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings # Import the settings instance

# Define the API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verifies the provided API key against the one in settings.
    Raises HTTPException if the key is invalid.
    """
    if api_key != settings.VERIFY_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key or missing X-API-Key header.",
        )
    return api_key
