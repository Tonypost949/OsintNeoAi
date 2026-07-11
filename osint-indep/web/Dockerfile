# Dockerfile for OSINT Independent Platform Web UI
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY web/package*.json ./
RUN npm ci --only=production

# Copy source
COPY web/ ./

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]