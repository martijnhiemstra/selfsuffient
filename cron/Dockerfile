# Python-based cron container for scheduled tasks
FROM python:3.11-slim

# Install pymongo for database access
RUN pip install --no-cache-dir pymongo

# Copy scripts
COPY daily_reminders.py /app/daily_reminders.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /app/daily_reminders.py

# Create log directory
RUN mkdir -p /var/log

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
