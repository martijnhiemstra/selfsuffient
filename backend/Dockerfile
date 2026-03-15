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

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Create uploads directory
RUN mkdir -p uploads

# Runtime environment variables (supply via docker run -e or docker-compose)
# Required:
#   MONGO_URL          - MongoDB connection string
#   DB_NAME            - Database name
# Security:
#   JWT_SECRET         - Secret for JWT tokens
#   CORS_ORIGINS       - Comma-separated allowed origins
# Admin (auto-created on first startup):
#   ADMIN_EMAIL        - Admin email
#   ADMIN_PASSWORD     - Admin password
#   ADMIN_NAME         - Admin display name
# Email/SMTP:
#   SMTP_HOST          - SMTP server hostname
#   SMTP_PORT          - SMTP port (default 465)
#   SMTP_USER          - SMTP username
#   SMTP_PASSWORD      - SMTP password
#   SMTP_FROM_EMAIL    - Sender email address
#   SMTP_FROM_NAME     - Sender display name
#   SMTP_VERIFY_SSL    - Verify SSL (default true)
# App:
#   APP_NAME           - Application name
#   APP_URL            - Public-facing frontend URL
#   MAX_UPLOAD_SIZE_MB - Max upload size in MB (default 5)
# Cron:
#   CRON_SCHEDULE      - Cron expression for daily reminders

EXPOSE 8001

# Use entrypoint script to start cron + uvicorn
ENTRYPOINT ["/app/entrypoint.sh"]
