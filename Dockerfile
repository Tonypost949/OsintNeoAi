# OSINTNeoAI Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10001 \
    STAGING_DIR=/app/data/staging

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Create staging directory
RUN mkdir -p /app/data/staging

# Expose port 10001
EXPOSE 10001

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:10001/ || exit 1

# Start Dynamic Genesis Webhook via uvicorn
CMD ["uvicorn", "scripts.dynamic_genesis_webhook:app", "--host", "0.0.0.0", "--port", "10001"]
