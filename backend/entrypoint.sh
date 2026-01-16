#!/bin/bash
set -e

# Setup cron for daily reminders if CRON_SCHEDULE is set
if [ -n "$CRON_SCHEDULE" ]; then
    echo "Setting up daily reminders cron: $CRON_SCHEDULE"
    
    # Create cron log file
    touch /var/log/cron.log
    
    # Export environment variables for cron
    printenv | grep -E "^(MONGO_URL|DB_NAME|SMTP_|APP_)" > /etc/environment
    
    # Create crontab entry
    echo "$CRON_SCHEDULE root cd /app && /usr/local/bin/python /app/daily_reminders.py >> /var/log/cron.log 2>&1" > /etc/cron.d/daily-reminders
    chmod 0644 /etc/cron.d/daily-reminders
    
    # Start cron daemon in background
    cron
    echo "Cron daemon started"
fi

# Start the FastAPI application
exec uvicorn server:app --host 0.0.0.0 --port 8001 --reload
