# Lightweight Alpine-based cron container
FROM alpine:3.19

# Install curl for making API calls
RUN apk add --no-cache curl

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create log directory
RUN mkdir -p /var/log

# Run as root (required for cron)
USER root

ENTRYPOINT ["/entrypoint.sh"]
