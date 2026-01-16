# Self-Sufficient Lifestyle App - Docker Setup

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Run with Docker Compose

1. **Clone the repository and navigate to the project directory**

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

### Environment Variables

Create a `.env` file in the root directory for custom configuration:

```env
# JWT Secret (change in production!)
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# MongoDB (optional - uses defaults if not set)
MONGO_URL=mongodb://mongodb:27017
DB_NAME=selfsufficient_db
```

### Common Commands

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

### Development Mode

For development with hot-reload:

```bash
# Backend only (with volume mount for hot-reload)
docker-compose up -d mongodb backend

# Run frontend locally
cd frontend
yarn install
yarn start
```

### Production Deployment

For production, update these settings:

1. Change `JWT_SECRET` to a secure random value
2. Update `CORS_ORIGINS` to your domain
3. Use proper SSL/TLS certificates
4. Consider using Docker Swarm or Kubernetes for scaling

```bash
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Troubleshooting

**MongoDB connection issues:**
```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

**Backend not starting:**
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

**Frontend build issues:**
```bash
# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend
```
