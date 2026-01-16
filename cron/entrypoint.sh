#!/bin/bash
set -e

# Configuration
CRON_SCHEDULE="${CRON_SCHEDULE:-0 7 * * *}"
LOG_FILE="/var/log/cron.log"

# Create log file
touch $LOG_FILE

echo "=============================================="
echo "Daily Reminders Cron Service"
echo "=============================================="
echo "Schedule: $CRON_SCHEDULE"
echo "Database: $MONGO_URL / $DB_NAME"
echo "SMTP Host: ${SMTP_HOST:-not configured}"
echo "Log file: $LOG_FILE"
echo "=============================================="

# Create crontab
cat > /etc/cron.d/daily-reminders << EOF
# Daily Reminders - Send task summary emails
# Schedule: $CRON_SCHEDULE
$CRON_SCHEDULE root /usr/local/bin/python /app/daily_reminders.py >> $LOG_FILE 2>&1

# Empty line required
EOF

# Set permissions
chmod 0644 /etc/cron.d/daily-reminders

# Apply crontab
crontab /etc/cron.d/daily-reminders

echo "Cron service started. Waiting for scheduled time..."
echo "To test manually: docker-compose exec cron python /app/daily_reminders.py"

# Start cron in foreground
exec cron -f
