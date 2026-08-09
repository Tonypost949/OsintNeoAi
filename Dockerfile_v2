# Dockerfile for Render.com deployment - OSINT Neo AI Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyMuPDF and other tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Render defaults to port 10000, but app expects 8080 or PORT env
ENV PORT=10000
EXPOSE 10000

# Run with gunicorn, pointing to the app in main.py
# main.py contains 'from api.main import app'
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app", "--timeout", "120"]
