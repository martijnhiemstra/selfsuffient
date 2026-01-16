# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including cron
RUN apt-get update && apt-get install -y \
    gcc \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install pymongo for the daily reminders script
RUN pip install --no-cache-dir pymongo

# Create entrypoint script inline (avoids permission issues with volume mounts)
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Setup cron for daily reminders if CRON_SCHEDULE is set\n\
if [ -n "$CRON_SCHEDULE" ]; then\n\
    echo "Setting up daily reminders cron: $CRON_SCHEDULE"\n\
    touch /var/log/cron.log\n\
    printenv | grep -E "^(MONGO_URL|DB_NAME|SMTP_|APP_)" > /etc/environment\n\
    echo "$CRON_SCHEDULE root cd /app && /usr/local/bin/python /app/daily_reminders.py >> /var/log/cron.log 2>&1" > /etc/cron.d/daily-reminders\n\
    chmod 0644 /etc/cron.d/daily-reminders\n\
    cron\n\
    echo "Cron daemon started"\n\
fi\n\
\n\
# Start the FastAPI application\n\
exec uvicorn server:app --host 0.0.0.0 --port 8001 --reload\n\
' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8001

# Use entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]
