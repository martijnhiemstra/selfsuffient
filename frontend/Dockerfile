# Frontend Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json ./
COPY yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile || yarn install

# Copy application code
COPY . .

# Build-time arguments (supply via --build-arg or docker-compose args)
# Required:
#   REACT_APP_BACKEND_URL - Backend API URL (baked into static build)
# Optional:
#   REACT_APP_APP_NAME    - Application name
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_APP_NAME
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_APP_NAME=$REACT_APP_APP_NAME

RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
