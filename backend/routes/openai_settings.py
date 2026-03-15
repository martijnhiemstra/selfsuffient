"""OpenAI Settings routes - User API key management."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from cryptography.fernet import Fernet
import os
import base64

from config import db
from services import get_current_user
from services.openai_analyzer import test_openai_connection, OpenAITransactionAnalyzer

router = APIRouter()

# Encryption key for storing API keys (generate if not exists)
ENCRYPTION_KEY = os.environ.get("OPENAI_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key and store it - in production this should be in env
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    
fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for storage"""
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key for use"""
    return fernet.decrypt(encrypted_key.encode()).decode()


class OpenAISettingsRequest(BaseModel):
    api_key: str
    model: str = "gpt-4o-mini"


class OpenAISettingsResponse(BaseModel):
    has_api_key: bool
    model: str
    api_key_preview: Optional[str] = None  # Show last 4 chars
    last_updated: Optional[str] = None


class TestKeyResponse(BaseModel):
    valid: bool
    message: str


@router.get("/openai/settings", response_model=OpenAISettingsResponse)
async def get_openai_settings(current_user: dict = Depends(get_current_user)):
    """Get current OpenAI settings for the user"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    
    has_key = bool(user.get("openai_api_key"))
    api_key_preview = None
    
    if has_key:
        try:
            decrypted = decrypt_api_key(user["openai_api_key"])
            api_key_preview = f"...{decrypted[-4:]}"
        except:
            api_key_preview = "****"
    
    return OpenAISettingsResponse(
        has_api_key=has_key,
        model=user.get("openai_model", "gpt-4o-mini"),
        api_key_preview=api_key_preview,
        last_updated=user.get("openai_updated_at")
    )


@router.post("/openai/settings", response_model=OpenAISettingsResponse)
async def save_openai_settings(
    data: OpenAISettingsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save OpenAI API key and model preference"""
    # Validate model
    if data.model not in OpenAITransactionAnalyzer.AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model. Choose from: {', '.join(OpenAITransactionAnalyzer.AVAILABLE_MODELS)}"
        )
    
    # Encrypt the API key
    encrypted_key = encrypt_api_key(data.api_key)
    now = datetime.now(timezone.utc).isoformat()
    
    # Update user
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "openai_api_key": encrypted_key,
            "openai_model": data.model,
            "openai_updated_at": now
        }}
    )
    
    return OpenAISettingsResponse(
        has_api_key=True,
        model=data.model,
        api_key_preview=f"...{data.api_key[-4:]}",
        last_updated=now
    )


@router.delete("/openai/settings")
async def delete_openai_settings(current_user: dict = Depends(get_current_user)):
    """Remove OpenAI API key"""
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$unset": {
            "openai_api_key": "",
            "openai_model": "",
            "openai_updated_at": ""
        }}
    )
    return {"message": "OpenAI settings removed"}


@router.post("/openai/test", response_model=TestKeyResponse)
async def test_openai_key(
    data: OpenAISettingsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Test if the provided OpenAI API key works"""
    result = await test_openai_connection(data.api_key, data.model)
    return TestKeyResponse(**result)


@router.get("/openai/models")
async def get_available_models(current_user: dict = Depends(get_current_user)):
    """Get list of available OpenAI models"""
    return {
        "models": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and cost-effective"},
            {"id": "gpt-4o", "name": "GPT-4o", "description": "Best quality, higher cost"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "High quality, balanced cost"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fastest, lowest cost"}
        ]
    }
