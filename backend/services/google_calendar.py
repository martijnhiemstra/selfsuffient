"""Google Calendar integration service."""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email"
]


def get_google_auth_url(client_id: str, client_secret: str, redirect_uri: str, state: str) -> str:
    """Generate Google OAuth authorization URL."""
    from urllib.parse import urlencode
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state
    }
    
    return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"


def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> Dict[str, Any]:
    """Exchange authorization code for tokens."""
    token_resp = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    })
    
    if token_resp.status_code != 200:
        raise Exception(f"Token exchange failed: {token_resp.text}")
    
    return token_resp.json()


def get_google_user_email(access_token: str) -> str:
    """Get user's email from Google."""
    resp = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if resp.status_code != 200:
        raise Exception(f"Failed to get user info: {resp.text}")
    
    return resp.json().get('email')


def get_credentials(tokens: Dict[str, Any], client_id: str, client_secret: str) -> Credentials:
    """Create Google credentials from stored tokens."""
    creds = Credentials(
        token=tokens.get('access_token'),
        refresh_token=tokens.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=GOOGLE_SCOPES
    )
    return creds


async def refresh_credentials_if_needed(creds: Credentials, db, user_id: str) -> Credentials:
    """Refresh credentials if expired and update in database."""
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleRequest())
            # Update stored tokens
            await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "google_calendar.tokens.access_token": creds.token
                }}
            )
        except Exception as e:
            logger.error(f"Failed to refresh Google credentials: {e}")
            raise
    return creds


def get_calendar_service(creds: Credentials):
    """Build Google Calendar service."""
    return build('calendar', 'v3', credentials=creds)


def create_calendar_event(
    service,
    summary: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    description: str = None,
    all_day: bool = False,
    event_id: str = None
) -> Dict[str, Any]:
    """Create or update a calendar event."""
    
    if all_day:
        # All-day event
        event_body = {
            'summary': summary,
            'start': {'date': start_time.strftime('%Y-%m-%d')},
            'end': {'date': (end_time or start_time + timedelta(days=1)).strftime('%Y-%m-%d')}
        }
    else:
        # Timed event
        if not end_time:
            end_time = start_time + timedelta(hours=1)
        
        event_body = {
            'summary': summary,
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'}
        }
    
    if description:
        event_body['description'] = description
    
    try:
        if event_id:
            # Try to update existing event
            try:
                result = service.events().update(
                    calendarId='primary',
                    eventId=event_id,
                    body=event_body
                ).execute()
                return result
            except Exception:
                # Event doesn't exist, create new
                pass
        
        # Create new event
        result = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()
        return result
    except Exception as e:
        logger.error(f"Failed to create/update calendar event: {e}")
        raise


def delete_calendar_event(service, event_id: str) -> bool:
    """Delete a calendar event."""
    try:
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        return True
    except Exception as e:
        logger.warning(f"Failed to delete calendar event {event_id}: {e}")
        return False


async def sync_task_to_calendar(db, user_id: str, task: Dict[str, Any]) -> Optional[str]:
    """Sync a task to Google Calendar. Returns the Google event ID."""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return None
    
    google_config = user.get("google_calendar", {})
    if not google_config.get("connected") or not google_config.get("sync_tasks"):
        return None
    
    tokens = google_config.get("tokens")
    client_id = google_config.get("client_id")
    client_secret = google_config.get("client_secret")
    
    if not all([tokens, client_id, client_secret]):
        return None
    
    try:
        creds = get_credentials(tokens, client_id, client_secret)
        creds = await refresh_credentials_if_needed(creds, db, user_id)
        service = get_calendar_service(creds)
        
        # Parse task due date
        due_date = task.get("due_date")
        if not due_date:
            return None
        
        if isinstance(due_date, str):
            start_time = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        else:
            start_time = due_date
        
        # Create event
        project = await db.projects.find_one({"id": task.get("project_id")}, {"_id": 0, "name": 1})
        project_name = project.get("name", "Unknown") if project else "Unknown"
        
        summary = f"[Task] {task.get('title', 'Untitled')}"
        description = f"Project: {project_name}\n\n{task.get('description', '')}"
        
        # Use existing google_event_id if available
        event_id = task.get("google_event_id")
        
        result = create_calendar_event(
            service=service,
            summary=summary,
            start_time=start_time,
            description=description,
            all_day=True,
            event_id=event_id
        )
        
        return result.get('id')
    except Exception as e:
        logger.error(f"Failed to sync task to calendar: {e}")
        return None


async def sync_routine_to_calendar(db, user_id: str, routine: Dict[str, Any], date: str) -> Optional[str]:
    """Sync a routine completion to Google Calendar."""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return None
    
    google_config = user.get("google_calendar", {})
    if not google_config.get("connected") or not google_config.get("sync_routines"):
        return None
    
    tokens = google_config.get("tokens")
    client_id = google_config.get("client_id")
    client_secret = google_config.get("client_secret")
    
    if not all([tokens, client_id, client_secret]):
        return None
    
    try:
        creds = get_credentials(tokens, client_id, client_secret)
        creds = await refresh_credentials_if_needed(creds, db, user_id)
        service = get_calendar_service(creds)
        
        # Parse routine time
        time_of_day = routine.get("time_of_day", "09:00")
        start_time = datetime.fromisoformat(f"{date}T{time_of_day}:00+00:00")
        end_time = start_time + timedelta(minutes=30)
        
        summary = f"[Routine] {routine.get('name', 'Untitled')}"
        description = routine.get('description', '')
        
        result = create_calendar_event(
            service=service,
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
            all_day=False
        )
        
        return result.get('id')
    except Exception as e:
        logger.error(f"Failed to sync routine to calendar: {e}")
        return None


async def delete_task_from_calendar(db, user_id: str, google_event_id: str) -> bool:
    """Delete a task's calendar event."""
    if not google_event_id:
        return False
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return False
    
    google_config = user.get("google_calendar", {})
    if not google_config.get("connected"):
        return False
    
    tokens = google_config.get("tokens")
    client_id = google_config.get("client_id")
    client_secret = google_config.get("client_secret")
    
    if not all([tokens, client_id, client_secret]):
        return False
    
    try:
        creds = get_credentials(tokens, client_id, client_secret)
        creds = await refresh_credentials_if_needed(creds, db, user_id)
        service = get_calendar_service(creds)
        
        return delete_calendar_event(service, google_event_id)
    except Exception as e:
        logger.error(f"Failed to delete task from calendar: {e}")
        return False
