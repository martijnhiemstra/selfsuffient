"""Authentication routes."""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta
import uuid
import secrets

from config import db, APP_URL, APP_NAME, logger
from models import (
    UserLogin, UserResponse, UserUpdateSettings, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, MessageResponse
)
from services import (
    hash_password, verify_password, create_token, get_current_user,
    send_email, get_password_reset_email_html
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user["password"]):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["email"])
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        is_admin=user.get("is_admin", False),
        daily_reminders=user.get("daily_reminders", False),
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        return MessageResponse(message="If the email exists, a reset link has been sent")
    
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.password_resets.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "token": reset_token,
        "expires_at": expires_at.isoformat(),
        "used": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    reset_url = f"{APP_URL}/reset-password?token={reset_token}"
    email_html = get_password_reset_email_html(reset_url, user.get("name", "User"))
    email_sent = send_email(data.email, f"Reset Your {APP_NAME} Password", email_html)
    
    if not email_sent:
        logger.info(f"Password reset token for {data.email}: {reset_token}")
        logger.info(f"Reset URL: {reset_url}")
    
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest):
    from fastapi import HTTPException
    
    reset_record = await db.password_resets.find_one({
        "token": data.token,
        "used": False
    }, {"_id": 0})
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    expires_at = datetime.fromisoformat(reset_record["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    hashed_password = hash_password(data.new_password)
    await db.users.update_one(
        {"id": reset_record["user_id"]},
        {"$set": {"password": hashed_password, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await db.password_resets.update_one(
        {"token": data.token},
        {"$set": {"used": True}}
    )
    
    return MessageResponse(message="Password reset successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        is_admin=current_user.get("is_admin", False),
        daily_reminders=current_user.get("daily_reminders", False),
        created_at=current_user["created_at"]
    )


@router.put("/settings", response_model=UserResponse)
async def update_user_settings(data: UserUpdateSettings, current_user: dict = Depends(get_current_user)):
    """Update user settings like daily reminders"""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one({"id": current_user["id"]}, {"$set": update_data})
    
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        is_admin=user.get("is_admin", False),
        daily_reminders=user.get("daily_reminders", False),
        created_at=user["created_at"]
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(data: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    from fastapi import HTTPException
    
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    
    if not verify_password(data.current_password, user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    hashed_password = hash_password(data.new_password)
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password": hashed_password, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return MessageResponse(message="Password changed successfully")
