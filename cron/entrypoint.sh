#!/bin/sh
set -e

# Replace environment variables in cron template
CRON_SCHEDULE="${CRON_SCHEDULE:-0 7 * * *}"
BACKEND_URL="${BACKEND_URL:-http://backend:8001}"

# Create the crontab file
cat > /etc/crontabs/root << EOF
# Daily Reminders - Send task summary emails
# Schedule: ${CRON_SCHEDULE} (default: 7:00 AM daily)
${CRON_SCHEDULE} /usr/bin/curl -sf -X POST ${BACKEND_URL}/api/cron/send-daily-reminders >> /var/log/cron.log 2>&1

# Rotate log weekly to prevent growth
0 0 * * 0 /usr/bin/find /var/log -name "cron.log" -size +10M -exec truncate -s 0 {} \;
EOF

# Create log file if it doesn't exist
touch /var/log/cron.log

echo "Cron service started with schedule: ${CRON_SCHEDULE}"
echo "Backend URL: ${BACKEND_URL}"
echo "Logs: /var/log/cron.log"

# Start cron in foreground
exec crond -f -l 2
