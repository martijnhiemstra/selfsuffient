"""Email services."""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    SMTP_FROM_EMAIL, SMTP_FROM_NAME, APP_NAME, APP_URL, logger
)


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via SMTP with SSL on port 465"""
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        logger.warning("SMTP not configured, email not sent")
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
        
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def get_test_email_html(user_name: str) -> str:
    """Generate test email HTML to verify SMTP settings"""
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
            .content {{ padding: 30px; }}
            .success-icon {{ font-size: 48px; text-align: center; margin-bottom: 20px; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{APP_NAME}</h1>
            </div>
            <div class="content">
                <div class="success-icon">✅</div>
                <h2 style="text-align: center; color: #2d5a3d;">Email Configuration Test Successful!</h2>
                <p>Hello {user_name},</p>
                <p>This is a test email to confirm that your email settings are configured correctly.</p>
                <p>If you received this email, your SMTP settings are working properly and you'll be able to:</p>
                <ul>
                    <li>Receive password reset emails</li>
                    <li>Receive daily reminder emails (if enabled)</li>
                </ul>
                <p>Best regards,<br>The {APP_NAME} Team</p>
            </div>
            <div class="footer">
                <p>This is a test email from {APP_NAME}.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_password_reset_email_html(reset_url: str, user_name: str) -> str:
    """Generate password reset email HTML"""
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
            .content {{ padding: 30px; }}
            .button {{ display: inline-block; background: #2d5a3d; color: white; text-decoration: none; padding: 14px 28px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{APP_NAME}</h1>
            </div>
            <div class="content">
                <p>Hello {user_name},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                <p>Best regards,<br>The {APP_NAME} Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message from {APP_NAME}.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_daily_reminder_email_html(user_name: str, startup_tasks: list, daily_tasks: list, shutdown_tasks: list) -> str:
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
                {'<p style="text-align: center; color: #666; margin-top: 30px;">No tasks scheduled for today. Enjoy your day!</p>' if not (startup_tasks or daily_tasks or shutdown_tasks) else ''}
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
