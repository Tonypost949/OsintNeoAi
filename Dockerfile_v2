# Dockerfile for OSINT Neo AI Backend with Security Tools
FROM debian:bookworm

WORKDIR /app

# Install Python 3.11 and base dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-dev \
    build-essential \
    libgl1-mesa-glx \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install security/OSINT tools from Debian repos
RUN apt-get update && apt-get install -y \
    nmap \
    hydra \
    netcat-openbsd \
    dnsrecon \
    curl \
    whois \
    dnsutils \
    traceroute \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the entire project
COPY . .

# Create reports processing directory
RUN mkdir -p /app/reports_output

# Expose port for Flask app (default, but Railway will override)
ENV PORT=10000
EXPOSE $PORT

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Run with gunicorn, pointing to the app in main.py using dynamic PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} main_v2:app --timeout 300 --workers 4"]
