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

To enable password reset emails, configure SMTP:

```env
# SMTP server settings (SSL on port 465)
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=Self-Sufficient Life
```

**Note:** If SMTP is not configured, password reset tokens are logged to the backend console (development mode).

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

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
# Backend only (with volume mount for hot-reload)
docker-compose up -d mongodb backend

# Run frontend locally
cd frontend
yarn install
yarn start
```

## Production Deployment

For production, ensure these settings:

1. **Change `JWT_SECRET`** to a secure random value (64+ characters)
2. **Configure `CORS_ORIGINS`** to your domain only
3. **Configure SMTP** for password reset functionality
4. **Set `APP_URL`** to your production frontend URL
5. Use proper SSL/TLS certificates (nginx/traefik)

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

**Frontend build issues:**
```bash
docker-compose build frontend --no-cache
docker-compose up -d frontend
```
