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

# Expose port
EXPOSE 8001

# Use entrypoint script to start cron + uvicorn
ENTRYPOINT ["/app/entrypoint.sh"]
