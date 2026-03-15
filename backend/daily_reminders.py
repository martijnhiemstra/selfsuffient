#!/usr/bin/env python3
"""
Daily Reminders Script
Sends morning task summary emails to users who have enabled daily reminders.
Runs directly with database access - no API endpoint needed.
"""

import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pymongo import MongoClient

# Configuration from environment
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'selfsufficient_db')

SMTP_HOST = os.environ.get('SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '465'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', '')
SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'Earthly Life')

APP_NAME = os.environ.get('APP_NAME', 'Earthly Life')
APP_URL = os.environ.get('APP_URL', 'http://localhost:3000')


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via SMTP with SSL on port 465"""
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        print(f"[WARN] SMTP not configured, skipping email to {to_email}")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, to_email, message.as_string())
        
        print(f"[OK] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {e}")
        return False


def get_email_html(user_name: str, startup_tasks: list, daily_tasks: list, shutdown_tasks: list) -> str:
    """Generate daily reminder email HTML"""
    
    def format_task_list(tasks: list, section_name: str, icon: str) -> str:
        if not tasks:
            return ""
        items = "".join([f'<li style="padding: 8px 0; border-bottom: 1px solid #eee;">{t["title"]}</li>' for t in tasks])
        return f"""
        <div style="margin: 20px 0;">
            <h3 style="color: #2d5a3d; margin-bottom: 10px;">{icon} {section_name}</h3>
            <ul style="list-style: none; padding: 0; margin: 0;">{items}</ul>
        </div>
        """
    
    startup_html = format_task_list(startup_tasks, "Start of Day Items", "🌅")
    daily_html = format_task_list(daily_tasks, "Today's Tasks", "📋")
    shutdown_html = format_task_list(shutdown_tasks, "End of Day Items", "🌙")
    
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    no_tasks_msg = ""
    if not (startup_tasks or daily_tasks or shutdown_tasks):
        no_tasks_msg = '<p style="text-align: center; color: #666; margin-top: 30px;">No tasks scheduled for today. Enjoy your day!</p>'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2d5a3d 0%, #4a7c59 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; }}
            .content {{ padding: 30px; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
            .button {{ display: inline-block; background: #2d5a3d; color: white; text-decoration: none; padding: 12px 24px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Good Morning, {user_name}!</h1>
                <p>{today}</p>
            </div>
            <div class="content">
                <p>Here's your daily task summary to help you stay on track:</p>
                {startup_html}
                {daily_html}
                {shutdown_html}
                {no_tasks_msg}
                <p style="text-align: center; margin-top: 30px;">
                    <a href="{APP_URL}/dashboard" class="button">Open Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>You're receiving this because you enabled daily reminders.</p>
                <p>Manage your preferences in <a href="{APP_URL}/settings">Settings</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """


def main():
    print(f"[{datetime.now().isoformat()}] Starting daily reminders...")
    
    # Connect to MongoDB
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        print(f"[OK] Connected to MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Find users with daily_reminders enabled
    users = list(db.users.find({"daily_reminders": True}, {"_id": 0, "password": 0}))
    
    if not users:
        print("[INFO] No users with daily reminders enabled")
        client.close()
        return
    
    print(f"[INFO] Found {len(users)} user(s) with daily reminders enabled")
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sent_count = 0
    
    for user in users:
        try:
            user_id = user["id"]
            user_email = user["email"]
            user_name = user.get("name", "User")
            
            # Get user's projects
            projects = list(db.projects.find({"user_id": user_id}, {"_id": 0}))
            project_ids = [p["id"] for p in projects]
            
            if not project_ids:
                print(f"[SKIP] User {user_email} has no projects")
                continue
            
            # Get startup tasks (Start of Day Items)
            startup_tasks = list(db.startup_routines.find(
                {"project_id": {"$in": project_ids}},
                {"_id": 0}
            ))
            
            # Get shutdown tasks (End of Day Items)
            shutdown_tasks = list(db.shutdown_routines.find(
                {"project_id": {"$in": project_ids}},
                {"_id": 0}
            ))
            
            # Get today's tasks
            today_start = f"{today}T00:00:00"
            today_end = f"{today}T23:59:59"
            daily_tasks = list(db.tasks.find({
                "project_id": {"$in": project_ids},
                "task_datetime": {"$gte": today_start, "$lte": today_end}
            }, {"_id": 0}))
            
            # Generate and send email
            email_html = get_email_html(user_name, startup_tasks, daily_tasks, shutdown_tasks)
            
            if send_email(user_email, f"Your {APP_NAME} Daily Tasks", email_html):
                sent_count += 1
            
        except Exception as e:
            print(f"[ERROR] Failed to process user {user.get('email')}: {e}")
    
    client.close()
    print(f"[{datetime.now().isoformat()}] Daily reminders complete. Sent: {sent_count}/{len(users)}")


if __name__ == "__main__":
    main()
