# Self-Sufficient Lifestyle App - Docker Setup

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Run with Docker Compose

1. **Copy environment file and configure:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - MongoDB: localhost:27017

4. **Seed the admin user:**
   ```bash
   curl -X POST http://localhost:8001/api/seed/admin
   ```

5. **Login with default credentials:**
   - Email: `admin@selfsufficient.app`
   - Password: `admin123`

## Services

| Service | Description | Port |
|---------|-------------|------|
| `frontend` | React SPA with Nginx | 3000 |
| `backend` | FastAPI REST API + Cron | 8001 |
| `mongodb` | MongoDB database | 27017 |

## Environment Variables

Create a `.env` file in the root directory. See `.env.example` for all options.

### Required Configuration

```env
# App name displayed throughout the application
APP_NAME=Self-Sufficient Life

# Public URL of your frontend
APP_URL=http://localhost:3000

# Security - CHANGE IN PRODUCTION!
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### Email Configuration (SMTP with SSL)

To enable password reset and daily reminder emails, configure SMTP:

```env
# SMTP server settings (SSL on port 465)
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=Self-Sufficient Life
```

**Note:** If SMTP is not configured, password reset tokens and daily reminders are logged to the backend console (development mode).

### Cron / Scheduled Tasks

Daily reminder emails are handled by a cron job inside the backend container:

```env
# Cron schedule (default: 7:00 AM daily)
# Format: minute hour day month weekday
CRON_SCHEDULE=0 7 * * *
```

**Examples:**
- `0 7 * * *` - 7:00 AM every day (default)
- `0 6 * * 1-5` - 6:00 AM on weekdays
- `30 8 * * *` - 8:30 AM every day
- `0 */4 * * *` - Every 4 hours

## Common Commands

```bash
# Start all services
docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View backend logs (includes cron output)
docker-compose logs -f backend

# View cron job logs specifically
docker-compose exec backend cat /var/log/cron.log

# Test daily reminders manually
docker-compose exec backend python /app/daily_reminders.py

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild containers
docker-compose up -d --build

# Access MongoDB shell
docker exec -it selfsufficient-mongodb mongosh
```

## Development Mode

For development with hot-reload:

```bash
# Start backend services only
docker-compose up -d mongodb backend

# Run frontend locally with hot-reload
cd frontend
yarn install
yarn start
```

## Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────┐
│   Frontend  │────▶│      Backend        │────▶│   MongoDB   │
│   (Nginx)   │     │  (FastAPI + Cron)   │     │             │
│   :3000     │     │      :8001          │     │   :27017    │
└─────────────┘     └─────────────────────┘     └─────────────┘
                            │
                            ├── API Server (uvicorn)
                            └── Cron Daemon (daily reminders)
```

## Production Deployment

For production, ensure these settings:

1. **Change `JWT_SECRET`** to a secure random value (64+ characters)
2. **Configure `CORS_ORIGINS`** to your domain only
3. **Configure SMTP** for email functionality
4. **Set `APP_URL`** to your production frontend URL
5. **Adjust `CRON_SCHEDULE`** for your timezone
6. Use proper SSL/TLS certificates (nginx/traefik)

```bash
# Generate a secure JWT secret
openssl rand -hex 64
```

## Troubleshooting

**MongoDB connection issues:**
```bash
docker-compose ps mongodb
docker-compose logs mongodb
```

**Backend not starting:**
```bash
docker-compose logs backend
docker-compose restart backend
```

**Email not sending:**
- Check SMTP credentials in `.env`
- Verify SMTP host and port (should be 465 for SSL)
- Check backend logs: `docker-compose logs backend | grep -i email`

**Cron not running:**
```bash
# Check if cron is running in the backend container
docker-compose exec backend ps aux | grep cron

# View cron logs
docker-compose exec backend cat /var/log/cron.log

# Test the daily reminders script manually
docker-compose exec backend python /app/daily_reminders.py
```

**Frontend build issues:**
```bash
docker-compose build frontend --no-cache
docker-compose up -d frontend
```
