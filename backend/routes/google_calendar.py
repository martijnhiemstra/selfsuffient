"""Google Calendar routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import os

from config import db
from services import get_current_user
from services.google_calendar import (
    get_google_auth_url,
    exchange_code_for_tokens,
    get_google_user_email,
    get_credentials,
    get_calendar_service,
    refresh_credentials_if_needed,
    sync_task_to_calendar,
    sync_routine_to_calendar
)

router = APIRouter()

# Get the frontend URL for redirects
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://eco-living-app.preview.emergentagent.com')


class GoogleCalendarSettings(BaseModel):
    client_id: str
    client_secret: str
    sync_tasks: bool = True
    sync_routines: bool = True
    sync_events: bool = True


class GoogleCalendarStatus(BaseModel):
    connected: bool
    google_email: Optional[str] = None
    sync_tasks: bool = False
    sync_routines: bool = False
    sync_events: bool = False
    has_credentials: bool = False


@router.get("/status", response_model=GoogleCalendarStatus)
async def get_calendar_status(current_user: dict = Depends(get_current_user)):
    """Get current Google Calendar connection status."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    
    google_config = user.get("google_calendar", {})
    
    return GoogleCalendarStatus(
        connected=google_config.get("connected", False),
        google_email=google_config.get("google_email"),
        sync_tasks=google_config.get("sync_tasks", False),
        sync_routines=google_config.get("sync_routines", False),
        sync_events=google_config.get("sync_events", False),
        has_credentials=bool(google_config.get("client_id") and google_config.get("client_secret"))
    )


@router.post("/settings")
async def save_calendar_settings(
    settings: GoogleCalendarSettings,
    current_user: dict = Depends(get_current_user)
):
    """Save Google Calendar credentials and sync settings."""
    now = datetime.now(timezone.utc).isoformat()
    
    # Get existing config to preserve tokens if already connected
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    existing_config = user.get("google_calendar", {})
    
    update_data = {
        "google_calendar.client_id": settings.client_id,
        "google_calendar.client_secret": settings.client_secret,
        "google_calendar.sync_tasks": settings.sync_tasks,
        "google_calendar.sync_routines": settings.sync_routines,
        "google_calendar.sync_events": settings.sync_events,
        "google_calendar.updated_at": now
    }
    
    # If credentials changed, disconnect
    if (existing_config.get("client_id") != settings.client_id or 
        existing_config.get("client_secret") != settings.client_secret):
        update_data["google_calendar.connected"] = False
        update_data["google_calendar.tokens"] = None
        update_data["google_calendar.google_email"] = None
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    return {"message": "Settings saved", "needs_reconnect": existing_config.get("client_id") != settings.client_id}


@router.get("/connect")
async def connect_google_calendar(current_user: dict = Depends(get_current_user)):
    """Start Google OAuth flow."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    google_config = user.get("google_calendar", {})
    
    client_id = google_config.get("client_id")
    client_secret = google_config.get("client_secret")
    
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=400, 
            detail="Please save your Google Client ID and Client Secret first"
        )
    
    # Generate state token for security
    state = f"{current_user['id']}:{uuid.uuid4()}"
    
    # Store state temporarily
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"google_calendar.oauth_state": state}}
    )
    
    # Build redirect URI
    redirect_uri = f"{FRONTEND_URL}/api/google-calendar/callback"
    
    auth_url = get_google_auth_url(client_id, client_secret, redirect_uri, state)
    
    return {"authorization_url": auth_url}


@router.get("/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...)
):
    """Handle Google OAuth callback."""
    # Extract user_id from state
    try:
        user_id = state.split(":")[0]
    except:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Verify state
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    google_config = user.get("google_calendar", {})
    stored_state = google_config.get("oauth_state")
    
    if stored_state != state:
        raise HTTPException(status_code=400, detail="State mismatch - possible CSRF attack")
    
    client_id = google_config.get("client_id")
    client_secret = google_config.get("client_secret")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Missing credentials")
    
    # Exchange code for tokens
    redirect_uri = f"{FRONTEND_URL}/api/google-calendar/callback"
    
    try:
        tokens = exchange_code_for_tokens(code, client_id, client_secret, redirect_uri)
    except Exception as e:
        # Redirect to settings with error
        return RedirectResponse(f"{FRONTEND_URL}/settings?google_error=token_exchange_failed")
    
    # Get user's Google email
    try:
        google_email = get_google_user_email(tokens.get("access_token"))
    except Exception as e:
        google_email = None
    
    # Save tokens and mark as connected
    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "google_calendar.tokens": tokens,
            "google_calendar.google_email": google_email,
            "google_calendar.connected": True,
            "google_calendar.connected_at": now,
            "google_calendar.oauth_state": None  # Clear state
        }}
    )
    
    # Redirect back to settings page
    return RedirectResponse(f"{FRONTEND_URL}/settings?google_connected=true")


@router.post("/disconnect")
async def disconnect_google_calendar(current_user: dict = Depends(get_current_user)):
    """Disconnect Google Calendar."""
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "google_calendar.connected": False,
            "google_calendar.tokens": None,
            "google_calendar.google_email": None
        }}
    )
    
    return {"message": "Google Calendar disconnected"}


@router.post("/sync-all-tasks")
async def sync_all_tasks(current_user: dict = Depends(get_current_user)):
    """Manually sync all tasks to Google Calendar."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    google_config = user.get("google_calendar", {})
    
    if not google_config.get("connected"):
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    if not google_config.get("sync_tasks"):
        raise HTTPException(status_code=400, detail="Task sync is disabled")
    
    # Get all tasks with due dates that aren't completed
    tasks = await db.tasks.find({
        "user_id": current_user["id"],
        "due_date": {"$ne": None},
        "status": {"$ne": "completed"}
    }, {"_id": 0}).to_list(1000)
    
    synced = 0
    failed = 0
    
    for task in tasks:
        try:
            event_id = await sync_task_to_calendar(db, current_user["id"], task)
            if event_id:
                # Update task with google event id
                await db.tasks.update_one(
                    {"id": task["id"]},
                    {"$set": {"google_event_id": event_id}}
                )
                synced += 1
        except Exception as e:
            failed += 1
    
    return {"message": f"Synced {synced} tasks, {failed} failed"}


@router.post("/sync-all-routines")
async def sync_all_routines(current_user: dict = Depends(get_current_user)):
    """Manually sync today's routines to Google Calendar."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    google_config = user.get("google_calendar", {})
    
    if not google_config.get("connected"):
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    if not google_config.get("sync_routines"):
        raise HTTPException(status_code=400, detail="Routine sync is disabled")
    
    # Get all active routines
    routines = await db.routine_tasks.find({
        "user_id": current_user["id"],
        "active": True
    }, {"_id": 0}).to_list(1000)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    synced = 0
    failed = 0
    
    for routine in routines:
        try:
            event_id = await sync_routine_to_calendar(db, current_user["id"], routine, today)
            if event_id:
                synced += 1
        except Exception as e:
            failed += 1
    
    return {"message": f"Synced {synced} routines for today, {failed} failed"}


@router.get("/test-connection")
async def test_connection(current_user: dict = Depends(get_current_user)):
    """Test if Google Calendar connection is working."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    google_config = user.get("google_calendar", {})
    
    if not google_config.get("connected"):
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    tokens = google_config.get("tokens")
    client_id = google_config.get("client_id")
    client_secret = google_config.get("client_secret")
    
    if not all([tokens, client_id, client_secret]):
        raise HTTPException(status_code=400, detail="Missing credentials or tokens")
    
    try:
        creds = get_credentials(tokens, client_id, client_secret)
        creds = await refresh_credentials_if_needed(creds, db, current_user["id"])
        service = get_calendar_service(creds)
        
        # Try to list calendars
        calendars = service.calendarList().list(maxResults=1).execute()
        
        return {
            "status": "ok",
            "message": "Connection successful",
            "primary_calendar": calendars.get("items", [{}])[0].get("summary", "Primary")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection test failed: {str(e)}")
